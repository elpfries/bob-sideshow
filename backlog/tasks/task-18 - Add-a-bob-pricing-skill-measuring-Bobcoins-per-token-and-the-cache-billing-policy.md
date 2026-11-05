---
id: TASK-18
title: >-
  Add a bob-pricing skill measuring Bobcoins per token and the cache-billing
  policy
status: Done
assignee:
  - '@claude'
created_date: '2026-11-05 01:35'
updated_date: '2026-11-05 01:39'
labels:
  - 'model:secondaire'
dependencies: []
documentation:
  - skills/bob-telemetry/SKILL.md
  - docs/bob-2.2.3-to-2.3.0.md
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A fifth shipped skill, bob-pricing, that reads ~/.bob/db/bob.db and answers three questions a Bob user asks about money: how many Bobcoins Bob charges per million context tokens (measured on every priced call, not assumed), whether tokens re-read from the prompt cache are billed at the full rate (on 2.3.0, 12/12 calls show cost = contextTokens x 2e-6 exactly, consecutive turns included, so no cache discount reaches the user), and how much that costs compared with a standard API provider that discounts cached input (Anthropic, OpenAI, Moonshot, DeepSeek style). Facts come from the 2.3.0 bundle: handleUsageStats builds spend with contextTokens = inputTokens + outputTokens (cached tokens included) and cost = raw.credits returned by the server (extractProviderCost); the stored _meta.spend keeps only {cost, contextTokens}. Public Bobcoin price: 0.50 USD overage, plan-effective 0.40/0.33/0.20 USD (Pro/Pro+/Ultra).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 skills/bob-pricing/ follows the repo conventions: SKILL.md with frontmatter name bob-pricing, scripts/bob_pricing.py (Python 3.8+, stdlib, read-only, offline) and an identical copy of scripts/_bobcheck.py (one shasum across all six skills)
- [x] #2 bob_pricing.py rate reports, per priced call and overall, the Bobcoins per million context tokens, fits the linear rate, and states clearly whether every call matches a single flat rate (max deviation printed)
- [x] #3 bob_pricing.py cache states explicitly whether cached tokens are billed at the full rate, using the evidence available (flat rate on consecutive turns of the same task within seconds; cacheRead absent from the stored spend) and names the build and source of each fact
- [x] #4 bob_pricing.py compare estimates what the same context tokens would have cost on a provider with a cache discount, with the cache share, input, cache-read and output prices as parameters (documented defaults), and prints the loss or gain versus Bob at the overage price and at each plan-effective price
- [x] #5 SKILL.md documents the measured rate (2.0 Bobcoins per million context tokens on 2.3.0), the cache finding, the USD conversion, the limits of the evidence (number of calls, context sizes, one account), and when to re-measure
- [x] #6 python3 -m py_compile passes on the new scripts, the script runs against the real installation, README.md lists the skill, CHANGELOG 0.5 section mentions it (v0.5 is not tagged yet)
- [x] #7 No personal data in examples or fixtures
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Mirror bob-telemetry: skills/bob-pricing/{SKILL.md, scripts/bob_pricing.py, scripts/_bobcheck.py (byte copy)}.
2. bob_pricing.py loads bob.db read-only (same open_db/load as bob_telemetry), iterates priced calls (agent + nested subagent spends), keeps cost and contextTokens; input/output when present (2.1.0-shaped rows).
3. Views: rate (per-call Bobcoins/M context tokens, fitted flat rate, max deviation, verdict single flat rate or not, classes), cache (consecutive-turn pairs of the same task: delta ctx vs delta cost, expected cost under a cache discount vs billed, explicit verdict), compare (parametrised provider: --cache-share --input --cache-read --output USD/M, defaults documented; USD per Bobcoin --usd-per-bobcoin default 0.50 plus plan table 0.40/0.333/0.20; prints Bob USD vs provider USD and the loss factor), all with --json.
4. Facts cited in SKILL.md and the docstring: 2.3.0 bundle handleUsageStats / extractProviderCost (contextTokens = input+output incl. cached; cost = raw.credits from the server), 12/12 calls at exactly 2e-6, limits (12 calls, 17-31K ctx, one account), re-measure trigger.
5. README list + example, CHANGELOG 0.5 bullet, py_compile, shasum check, run against the real DB.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verification 2026-11-05 on the real install (bob-code 2.3.0, schema 013): rate -> 12 calls, fitted 2.0000 Bobcoins/M, worst call 0.000 % off, ONE FLAT RATE; cache -> 9 follow-up turns (2-41 s), 9/9 billed at the full rate, verdict FULL RATE, cacheRead not stored; compare --bobcoins 950 -> 475 USD overage, policy alone 4.3x overpaid at 85 % cache share, DeepSeek Flash 10.5x cheaper, Sonnet 5.5 / K3.1 Pro on par, Opus 5.5 and K3 dearer. py_compile on all skills OK, node --check OK, shasum of the six _bobcheck.py = one hash, install.sh ships bob-pricing, grep for personal data empty, --task zzz edge case prints the no-call message. Bundle facts (handleUsageStats contextTokens = input+output incl. cached; extractProviderCost = raw.credits) read in private/baseline-2.3.0 extension.js.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added skills/bob-pricing (SKILL.md, scripts/bob_pricing.py, identical _bobcheck.py) with three views: rate (Bobcoins per million context tokens per call, fitted flat rate, deviation, USD by plan), cache (follow-up turns vs flat rate, explicit FULL RATE / DISCOUNT SEEN / UNDETERMINED verdict), compare (provider table with cache discount, loss due to the policy alone, --bobcoins/--tokens/--provider/custom prices). README lists the skill, CHANGELOG 0.5 has a bullet, bob-telemetry SKILL.md no longer says the unit price cannot be measured. Verified on the real 2.3.0 database: 2.0 Bobcoins/M exact on 12/12 calls, 9/9 follow-up turns at the full rate.
<!-- SECTION:FINAL_SUMMARY:END -->
