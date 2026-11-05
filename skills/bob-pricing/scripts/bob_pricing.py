#!/usr/bin/env python3
"""What a Bobcoin buys: Bobcoins per token, the cache-billing policy, and the cost of that policy.

  bob_pricing.py rate    [--task PREFIX] [--since YYYY-MM-DD] [--db PATH] [--json]
  bob_pricing.py cache   [--gap SECONDS] [--discount 0.10] [--task PREFIX] [--since DATE] [--db PATH] [--json]
  bob_pricing.py compare [--provider NAME | --input X --cache-read X --output X] [--cache-share 0.85]
                         [--output-share 0.05] [--bobcoins N | --tokens N] [--usd-per-bobcoin 0.50] [--json]

Read-only; Python 3.8+, standard library only, no network.

Where the numbers come from (bob-code 2.3.0, build 1.126.0+bob2.3.0.20261026121409, dist/extension.js):
- `handleUsageStats` builds the per-call spend as {input, output, cacheRead, cacheWrite, cost, contextTokens,
  reasoningTokens} with contextTokens = inputTokens + outputTokens. inputTokens is the provider's total prompt
  count, cached tokens included (cached_tokens is read separately into cacheRead).
- `cost` is not computed locally: `extractProviderCost` returns `raw.credits` from the server response
  (the second path reads providerMetadata.openrouter.usage.cost). It is the bill, in Bobcoins.
- The stored message keeps only {cost, contextTokens} (since 2.2.0; checked on 2.2.3 and 2.3.0), so cacheRead
  never reaches bob.db. The views below work from cost and contextTokens alone.

Measured on live traffic, 2026-11-05, one account, 12 priced calls (4 on 2.2.3, 8 on 2.3.0), contexts of
17,632 to 31,456 tokens: cost = contextTokens x 2e-6 on every call, to the sixth decimal, including turns 11
and 13 seconds apart on the same task where a prompt cache would have applied. So 2.0 Bobcoins per million
context tokens, and no cache discount reaches the user. The 0.833 economy rate seen on 2.1.0 (explore
subagents) could not be re-measured: no subagent call in that database.

Public Bobcoin price (bob.ibm.com/docs/ide/account/bobcoins, read 2026-11-05): 0.50 USD per Bobcoin in
overage and in Enterprise packs (1,000 for 500 USD; overage packs 550 USD); plans Pro 20 USD / 50 Bobcoins,
Pro+ 60 USD / 180, Ultra 200 USD / 1,000 (plan-effective 0.40, 0.333, 0.20 USD per Bobcoin).
"""
import argparse
import collections
import datetime as dt
import json
import os
import shutil
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bobcheck  # noqa: E402

DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".bob", "db", "bob.db")
FLAT_TOLERANCE = 0.005  # 0.5 %: a call further than this from the fitted rate breaks the "single flat rate" verdict

USD_PER_BOBCOIN = 0.50
PLANS = [("overage / pack", 0.50), ("Pro 20 USD / 50", 0.40), ("Pro+ 60 USD / 180", 60 / 180), ("Ultra 200 USD / 1000", 0.20)]

# USD per million tokens, standard tier, as published on the date given. input / cache read / output.
PROVIDERS = {
    "claude-opus-5.5": (4.00, 0.20, 20.00, "Anthropic price table, 2026-10-06"),
    "claude-sonnet-5.5": (2.00, 0.20, 10.00, "Anthropic price table, 2026-10-06"),
    "gpt-6.1-sol": (2.00, 0.10, 10.00, "openai.com, Introducing GPT-6.1 Sol, read 2026-11-05"),
    "gpt-6.1-terra": (1.00, 0.05, 5.00, "OpenAI pricing via requesty.ai, read 2026-11-05"),
    "kimi-k3": (3.00, 0.30, 15.00, "platform.moonshot.ai via cloudzero.com, read 2026-11-05"),
    "kimi-k3.1-pro": (2.00, 0.20, 10.00, "benchlm.ai Moonshot pricing, read 2026-11-05"),
    "deepseek-flash": (0.30, 0.006, 1.20, "DeepSeek V4.1 Flash peak hours, benchlm.ai, read 2026-11-05"),
    "deepseek-flash-offpeak": (0.15, 0.003, 0.60, "DeepSeek V4.1 Flash off-peak (-50 %), benchlm.ai, read 2026-11-05"),
    "composer-2.5": (0.50, 0.20, 2.50, "Cursor Composer 2.5 Standard, datacamp.com, read 2026-11-05"),
}


def ts(ms):
    return dt.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S") if ms else "-"


def open_db(path):
    if not os.path.isfile(path):
        sys.exit(f"database not found: {path}")
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        con.execute("select count(*) from sqlite_master")
        return con
    except sqlite3.OperationalError:
        tmp = tempfile.mkdtemp(prefix="bob-sideshow-")
        for suf in ("", "-wal", "-shm"):
            if os.path.exists(path + suf):
                shutil.copy2(path + suf, os.path.join(tmp, "bob.db" + suf))
        return sqlite3.connect(os.path.join(tmp, "bob.db"))


def load_calls(con, since_ms, task_prefix):
    """Every priced call: agent calls and the calls nested in subagent messages."""
    con.row_factory = sqlite3.Row
    tasks = {}
    for r in con.execute("select id, parent_id, updated_at from tasks"):
        if since_ms and (r["updated_at"] or 0) < since_ms:
            continue
        if task_prefix and not r["id"].startswith(task_prefix):
            continue
        tasks[r["id"]] = dict(r)
    calls = []
    for r in con.execute("select task_id, created_at, data from messages order by created_at"):
        if r["task_id"] not in tasks:
            continue
        try:
            d = json.loads(r["data"])
        except Exception:
            continue
        meta = d.get("_meta") or {}
        nested = d.get("messages") or []
        if meta.get("spend") and not nested:
            calls.append(_call(r["task_id"], "agent", meta.get("timestamp") or r["created_at"], meta["spend"]))
        for sm in nested:
            sme = sm.get("_meta") or {}
            if sme.get("spend"):
                calls.append(_call(r["task_id"], "subagent " + str(meta.get("agentType") or "?"),
                                   sme.get("timestamp") or r["created_at"], sme["spend"]))
    calls = [c for c in calls if c["ctx"] and c["cost"] is not None]
    calls.sort(key=lambda c: c["ts"])
    return calls


def _call(task, who, when, sp):
    ctx = sp.get("contextTokens") or ((sp.get("input") or 0) + (sp.get("output") or 0)) or None
    return {"task": task, "who": who, "ts": when, "ctx": ctx, "cost": sp.get("cost"),
            "tokensStored": ("input" in sp) or ("output" in sp), "cacheReadStored": "cacheRead" in sp,
            "rate": (sp.get("cost") / ctx * 1e6) if ctx and sp.get("cost") is not None else None}


def fit(calls):
    """Flat rate fitted on the totals, and how far the worst call sits from it."""
    tot_cost = sum(c["cost"] for c in calls)
    tot_ctx = sum(c["ctx"] for c in calls)
    rate = tot_cost / tot_ctx * 1e6 if tot_ctx else None
    dev = max((abs(c["rate"] - rate) / rate for c in calls), default=0.0) if rate else None
    return {"calls": len(calls), "bobcoins": tot_cost, "contextTokens": tot_ctx, "ratePerM": rate,
            "maxDeviation": dev, "flat": dev is not None and dev <= FLAT_TOLERANCE}


def clusters(calls):
    by = collections.defaultdict(list)
    for c in calls:
        by[round(c["rate"], 2)].append(c)
    return [{"ratePerM": k, "calls": len(v), "who": sorted(set(c["who"] for c in v))} for k, v in sorted(by.items())]


def table(rows, cols):
    if not rows:
        print("  (none)")
        return
    w = [max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols]
    print("  " + "  ".join(c.ljust(x) for c, x in zip(cols, w)))
    for r in rows:
        print("  " + "  ".join(str(r.get(c, "")).ljust(x) for c, x in zip(cols, w)))


def cmd_rate(calls, a):
    f = fit(calls)
    out = {**f, "clusters": clusters(calls), "usdPerMillion": {n: (f["ratePerM"] or 0) * p for n, p in PLANS},
           "calls_": [{"time": ts(c["ts"]), "task": c["task"][:8], "who": c["who"], "ctx": c["ctx"], "bobcoins": c["cost"],
                       "ratePerM": c["rate"]} for c in calls]}
    if a.json:
        print(json.dumps(out, indent=2))
        return
    if not calls:
        print("no priced call in the database (Bob purges tasks after tasks.retentionDays, 30 by default)")
        return
    table([{"time": r["time"], "task": r["task"], "who": r["who"], "ctx": f"{r['ctx']:,}", "Bobcoins": f"{r['bobcoins']:.6f}",
            "Bobcoins/M": f"{r['ratePerM']:.4f}"} for r in out["calls_"]], ["time", "task", "who", "ctx", "Bobcoins", "Bobcoins/M"])
    print(f"\n{f['calls']} priced calls, {f['bobcoins']:.4f} Bobcoins for {f['contextTokens']:,} context tokens")
    print(f"fitted rate: {f['ratePerM']:.4f} Bobcoins per million context tokens "
          f"(1 Bobcoin = {1e6 / f['ratePerM']:,.0f} tokens); worst call {f['maxDeviation'] * 100:.3f} % off")
    if f["flat"]:
        print("verdict: ONE FLAT RATE — every call is billed contextTokens x rate; no call deviates by more than "
              f"{FLAT_TOLERANCE * 100:.1f} %")
    else:
        print("verdict: NOT a single flat rate — rates differ by more than 0.5 %; see the clusters (a second class, or billing changed)")
    table([{"Bobcoins/M": f"{c['ratePerM']:.2f}", "calls": c["calls"], "who": ", ".join(c["who"])} for c in out["clusters"]],
          ["Bobcoins/M", "calls", "who"])
    print("\nUSD per million context tokens by Bobcoin price:")
    table([{"plan": n, "USD/Bobcoin": f"{p:.3f}", "USD/M tokens": f"{(f['ratePerM'] or 0) * p:.3f}"} for n, p in PLANS],
          ["plan", "USD/Bobcoin", "USD/M tokens"])
    print("source: cost is the server's `credits` field (extractProviderCost, 2.3.0 bundle); contextTokens = input + output,"
          " cached tokens included (handleUsageStats)")


def cmd_cache(calls, a):
    """Consecutive turns of one task: with a prompt cache, turn N+1 should cost less than contextTokens x rate."""
    f = fit(calls)
    rate = f["ratePerM"]
    pairs = []
    by_task = collections.defaultdict(list)
    for c in calls:
        by_task[(c["task"], c["who"])].append(c)
    for (task, who), seq in by_task.items():
        for p, q in zip(seq, seq[1:]):
            gap = (q["ts"] - p["ts"]) / 1000
            if gap > a.gap or q["ctx"] <= p["ctx"]:
                continue
            full = q["ctx"] * rate / 1e6
            discounted = (p["ctx"] * a.discount + (q["ctx"] - p["ctx"])) * rate / 1e6
            pairs.append({"task": task[:8], "who": who, "gap_s": gap, "ctxBefore": p["ctx"], "ctxAfter": q["ctx"],
                          "billed": q["cost"], "ifFullRate": full, "ifCacheDiscount": discounted,
                          "billedAtFullRate": abs(q["cost"] - full) <= FLAT_TOLERANCE * full})
    stored = any(c["cacheReadStored"] for c in calls)
    n_full = sum(1 for p in pairs if p["billedAtFullRate"])
    n_less = sum(1 for p in pairs if p["billed"] < p["ifFullRate"] * (1 - FLAT_TOLERANCE))
    verdict = ("UNDETERMINED: no consecutive turns within the gap" if not pairs else
               "FULL RATE: cached tokens are billed like fresh ones (or nothing is cached) — every re-read token costs the flat rate again"
               if n_full == len(pairs) else
               "DISCOUNT SEEN: some follow-up turns cost less than contextTokens x rate — a cache discount reaches the user"
               if n_less else "MIXED: see the pairs")
    out = {"ratePerM": rate, "pairs": pairs, "pairsAtFullRate": n_full, "pairsBelowFullRate": n_less,
           "cacheReadStoredInDb": stored, "verdict": verdict}
    if a.json:
        print(json.dumps(out, indent=2))
        return
    if not calls:
        print("no priced call in the database")
        return
    print(f"flat rate {rate:.4f} Bobcoins/M; follow-up turns of the same task within {a.gap:.0f} s, "
          f"expected bill if the previous context were cached at {a.discount * 100:.0f} % of the price:\n")
    table([{"task": p["task"], "who": p["who"], "gap": f"{p['gap_s']:.0f}s", "ctx before": f"{p['ctxBefore']:,}",
            "ctx after": f"{p['ctxAfter']:,}", "billed": f"{p['billed']:.6f}", "full rate": f"{p['ifFullRate']:.6f}",
            "with cache": f"{p['ifCacheDiscount']:.6f}", "billed =": "full rate" if p["billedAtFullRate"] else "LESS"}
           for p in pairs], ["task", "who", "gap", "ctx before", "ctx after", "billed", "full rate", "with cache", "billed ="])
    print(f"\n{len(pairs)} follow-up turns: {n_full} billed at the full rate, {n_less} below it")
    print("verdict: " + verdict)
    print("stored spend carries cacheRead: " + ("yes" if stored else
          "no — bob.db keeps {cost, contextTokens} only (since 2.2.0), so 'not cached' and 'cached but not discounted' "
          "cannot be told apart locally; the bill is the same either way"))
    print("sources: cost = server `credits` (extractProviderCost), contextTokens = input + output incl. cached tokens "
          "(handleUsageStats), bob-code 2.3.0 bundle; measured 2026-11-05 on 12 calls, 17-31K tokens, one account")


def blended(prices, cache_share, output_share):
    inp, cache, out = prices
    fresh = max(0.0, 1.0 - cache_share - output_share)
    return cache_share * cache + fresh * inp + output_share * out


def cmd_compare(calls, a):
    f = fit(calls) if calls else {"ratePerM": None, "bobcoins": 0, "contextTokens": 0, "calls": 0}
    rate = f["ratePerM"] or 2.0
    how = f"the measured {rate:.3f}" if f["ratePerM"] else "the documented 2.0 (no priced call in the database)"
    if a.bobcoins is not None:
        bobcoins = a.bobcoins
        tokens = bobcoins / rate * 1e6
        basis = f"{bobcoins:g} Bobcoins (given) at {how} Bobcoins/M"
    elif a.tokens is not None:
        tokens = a.tokens
        bobcoins = tokens * rate / 1e6
        basis = f"{tokens:,.0f} context tokens (given) at {how} Bobcoins/M"
    elif not calls:
        sys.exit("no priced call in the database; give --bobcoins N or --tokens N")
    else:
        tokens, bobcoins = f["contextTokens"], f["bobcoins"]
        basis = f"{f['calls']} priced calls in the database"
    if a.provider:
        if a.provider not in PROVIDERS:
            sys.exit("unknown provider; choose from " + ", ".join(sorted(PROVIDERS)))
        rows = [(a.provider, PROVIDERS[a.provider])]
    elif a.input is not None:
        rows = [("custom", (a.input, a.cache_read, a.output, "given on the command line"))]
    else:
        rows = sorted(PROVIDERS.items())
    bob_rows = [{"plan": n, "usdPerBobcoin": p, "usdPerM": rate * p, "usd": bobcoins * p} for n, p in PLANS]
    bob_overage = rate * a.usd_per_bobcoin
    prov_rows = []
    for name, (inp, cache, out, src) in rows:
        per_m = blended((inp, cache, out), a.cache_share, a.output_share)
        prov_rows.append({"provider": name, "input": inp, "cacheRead": cache, "output": out, "blendedUsdPerM": per_m,
                          "usd": tokens * per_m / 1e6, "bobOverageOverProvider": bob_overage / per_m if per_m else None,
                          "bobUltraOverProvider": rate * 0.20 / per_m if per_m else None, "source": src})
    # The cache policy alone: Bob's own rate, but with cached re-reads at `discount` of the price.
    policy_factor = (1 - a.cache_share) + a.cache_share * a.discount
    policy = {"discount": a.discount, "bobcoinsWithDiscount": bobcoins * policy_factor,
              "bobcoinsLostToPolicy": bobcoins * (1 - policy_factor), "overpayFactor": 1 / policy_factor}
    out = {"basis": basis, "contextTokens": tokens, "bobcoins": bobcoins, "ratePerM": rate,
           "mix": {"cacheShare": a.cache_share, "outputShare": a.output_share, "freshShare": round(1 - a.cache_share - a.output_share, 6)},
           "cachePolicy": policy, "bob": bob_rows, "providers": prov_rows}
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"basis: {basis} = {tokens:,.0f} context tokens, {bobcoins:,.2f} Bobcoins")
    print(f"Bob bills every context token at {rate:.3f} Bobcoins/M, cached or not:")
    table([{"plan": r["plan"], "USD/Bobcoin": f"{r['usdPerBobcoin']:.3f}", "USD/M": f"{r['usdPerM']:.3f}", "USD": f"{r['usd']:,.2f}"}
           for r in bob_rows], ["plan", "USD/Bobcoin", "USD/M", "USD"])
    print(f"\nthe cache policy alone: at Bob's own rate but with cached re-reads at {a.discount * 100:.0f} % of the price "
          f"({a.cache_share * 100:.0f} % of context tokens), the same work would cost {policy['bobcoinsWithDiscount']:,.2f} Bobcoins "
          f"instead of {bobcoins:,.2f} — {policy['bobcoinsLostToPolicy']:,.2f} Bobcoins "
          f"({policy['overpayFactor']:.1f}× overpaid) go to re-reading tokens a standard provider would discount")
    print(f"\nprovider with a cache discount, token mix {a.cache_share * 100:.0f} % cache read / "
          f"{(1 - a.cache_share - a.output_share) * 100:.0f} % fresh input / {a.output_share * 100:.0f} % output "
          "(an assumption about agentic traffic, not a measurement; change it with --cache-share / --output-share):")
    table([{"provider": r["provider"], "in": f"{r['input']:.2f}", "cache": f"{r['cacheRead']:.3f}", "out": f"{r['output']:.2f}",
            "blended USD/M": f"{r['blendedUsdPerM']:.3f}", "USD": f"{r['usd']:,.2f}",
            "Bob overage ×": f"{r['bobOverageOverProvider']:.1f}", "Bob Ultra ×": f"{r['bobUltraOverProvider']:.1f}"}
           for r in prov_rows], ["provider", "in", "cache", "out", "blended USD/M", "USD", "Bob overage ×", "Bob Ultra ×"])
    print("\n'Bob overage ×' = what Bob charges at 0.50 USD/Bobcoin divided by what that provider would charge for the same tokens;"
          " above 1 is Bob's loss from billing cached tokens at the full rate, below 1 Bob is cheaper.")
    for r in prov_rows:
        print(f"  {r['provider']}: {r['source']}")


VIEWS = {"rate": cmd_rate, "cache": cmd_cache, "compare": cmd_compare}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("view", choices=sorted(VIEWS))
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--task", help="task id prefix")
    ap.add_argument("--since", help="tasks updated on/after YYYY-MM-DD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gap", type=float, default=120.0, help="cache: max seconds between two turns of one task (120)")
    ap.add_argument("--discount", type=float, default=0.10, help="cache, compare: cached-token price as a fraction of the fresh price (0.10)")
    ap.add_argument("--provider", help="compare: one of " + ", ".join(sorted(PROVIDERS)) + " (default: all)")
    ap.add_argument("--input", type=float, help="compare: custom provider USD per million fresh input tokens")
    ap.add_argument("--cache-read", type=float, default=0.0, help="compare: custom provider USD per million cached input tokens")
    ap.add_argument("--output", type=float, default=0.0, help="compare: custom provider USD per million output tokens")
    ap.add_argument("--cache-share", type=float, default=0.85, help="compare: share of context tokens that are cache re-reads (0.85)")
    ap.add_argument("--output-share", type=float, default=0.05, help="compare: share of context tokens that are output (0.05)")
    ap.add_argument("--bobcoins", type=float, help="compare: price this many Bobcoins instead of the database")
    ap.add_argument("--tokens", type=float, help="compare: price this many context tokens instead of the database")
    ap.add_argument("--usd-per-bobcoin", type=float, default=USD_PER_BOBCOIN, help="compare: overage price (0.50)")
    _bobcheck.add_arguments(ap)
    a = ap.parse_args()
    if a.cache_share + a.output_share > 1:
        sys.exit("--cache-share plus --output-share must not exceed 1")
    _bobcheck.check("bob_pricing", db_path=a.db, quiet=a.no_version_check, strict=a.strict)
    since_ms = int(dt.datetime.strptime(a.since, "%Y-%m-%d").timestamp() * 1000) if a.since else None
    VIEWS[a.view](load_calls(open_db(a.db), since_ms, a.task), a)


if __name__ == "__main__":
    main()
