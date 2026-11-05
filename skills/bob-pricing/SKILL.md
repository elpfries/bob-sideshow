---
name: bob-pricing
description: Use when the user asks what a Bobcoin is worth in tokens or dollars, how many Bobcoins IBM Bob charges per million tokens, whether tokens re-read from the prompt cache are billed at the full rate, or how Bob's billing compares with an API provider that discounts cached input — measured from the local database ~/.bob/db/bob.db, not assumed.
---

# Bob pricing

`python3 "<skill-dir>/scripts/bob_pricing.py" <view> [options] [--db PATH] [--json]`

| view | answers |
|---|---|
| `rate` | Bobcoins per million context tokens, call by call and fitted; is it one flat rate? USD per million by plan |
| `cache` | are cached tokens billed at the full rate? (follow-up turns of one task vs the flat rate) |
| `compare` | what the same tokens cost on a provider with a cache discount, and the loss due to Bob's policy |

Options: `--task PREFIX`, `--since YYYY-MM-DD`; `cache`: `--gap SECONDS` (120), `--discount` (0.10);
`compare`: `--provider NAME` or `--input/--cache-read/--output` USD per million, `--cache-share` (0.85),
`--output-share` (0.05), `--bobcoins N` or `--tokens N` to price a figure instead of the database,
`--usd-per-bobcoin` (0.50).

When explaining (build 2.3.0 = `1.126.0+bob2.3.0.20261026121409` unless a bullet says otherwise):

- **The rate.** Measured 2026-11-05 on live traffic: **2.0 Bobcoins per million context tokens**, exact to the
  sixth decimal on 12 of 12 priced calls (4 made by 2.2.3 on 2026-10-19, 8 by 2.3.0 on 2026-11-02/03;
  contexts 17,632 to 31,456 tokens; one account; agent calls only). One Bobcoin = 500,000 context tokens.
  `rate` re-measures this on whatever the database holds and says whether every call still fits one flat
  rate (tolerance 0.5 %); a second cluster means a second model class or a price change — report it.
- **What is counted.** Source: `dist/extension.js` of 2.3.0, `handleUsageStats`. `contextTokens` is
  `inputTokens + outputTokens`, where `inputTokens` is the provider's full prompt count, **cached tokens
  included** (`cached_tokens` / `cacheReadTokens` is read separately into `cacheRead`). So Bob bills the
  whole context on every turn: a session at 100K tokens costs 0.2 Bobcoin per turn, and the price of a turn
  grows with the length of the conversation.
- **Who sets the price.** `cost` is not computed on the client: `extractProviderCost` returns the `credits`
  field of the server's response (the other code path reads `providerMetadata.openrouter.usage.cost`). The
  stored figure is the bill in Bobcoins, so the measurement is of what IBM charges, not of a local formula.
- **Cache: billed at the full rate.** On the 9 follow-up turns 2 to 41 seconds apart within one task (the
  case a prompt cache is made for: 18,304 → 18,898 → 20,051 tokens, same prefix), every turn cost exactly
  `contextTokens × 2e-6`. With a standard 90 % discount on cached input the second turn would have cost
  0.0048 Bobcoin; it cost 0.0378. Either the upstream provider caches and IBM keeps the discount, or nothing
  is cached: the bill is the same for the user, and the database cannot tell the two apart because
  `_meta.spend` keeps only `{cost, contextTokens}` since 2.2.0 (`cacheRead` is computed, never stored).
  `cache` prints that verdict from the data it finds; it says UNDETERMINED when no two turns of a task fall
  within `--gap`.
- **The loss.** With Bob's own rate but cached re-reads at 10 % of the price, and 85 % of context tokens
  being re-reads (an assumption about agentic traffic, not a measurement — change `--cache-share`), the
  same work costs 23.5 % of what Bob bills: **4.3× overpaid** on the re-read tokens. Against real providers
  (`compare`, prices as published on the date each row cites, standard tier, long-context surcharges
  ignored): at 0.50 USD per Bobcoin Bob is on par with Claude Sonnet 5.5 and Kimi K3.1 Pro, 1.3× GPT-6.1 Sol,
  2.5× GPT-6.1 Terra, 2.9× Composer 2.5, 10× DeepSeek Flash (21× off-peak), and cheaper than Claude Opus
  5.5 and Kimi K3. Bob Ultra (0.20 USD per Bobcoin) divides these by 2.5.
- **USD conversion** (bob.ibm.com/docs/ide/account/bobcoins, read 2026-11-05): 0.50 USD per Bobcoin in
  overage and Enterprise packs (1,000 for 500 USD, 550 USD through overage packs, packs expire after a year);
  Pro 20 USD / 50 Bobcoins, Pro+ 60 / 180, Ultra 200 / 1,000, so 0.40, 0.33 and 0.20 USD plan-effective.
  Per million context tokens: 1.00 USD overage, 0.80 Pro, 0.67 Pro+, 0.40 Ultra.
- **What this does not say.** Bob stores no model name, so the rate is per *tier*, not per model; the
  0.833 Bobcoins/M economy rate (explore subagents) was measured on 2.1.0 and has not been seen since (no
  subagent call in the 2.3.0 database). Twelve calls on one account cover contexts up to 31K: a discount
  that only applied above a larger prefix, or to another tier, is not excluded. Re-measure (`rate` then
  `cache`) after any Bob update, on a long session (100K+ context, several quick turns), and whenever a
  subagent has run; a single call below the flat rate on a follow-up turn is enough to prove a discount.

The script prints task id prefixes, timestamps, token counts and Bobcoins, never message bodies.
