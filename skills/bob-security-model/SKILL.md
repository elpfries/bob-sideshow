---
name: bob-security-model
description: Use when the user asks why IBM Bob asks for approval, how approved or denied command patterns match (prefix, wildcard, case), what "Security warning" or requiresSecurityApproval means, whether a yolo-like mode exists (it does not in the IDE), which approval settings exist and what still prompts with the most permissive ones, or whether a given command would be auto-approved.
---

# Bob security model

Reference notes verified on bob-code 2.3.0 (build `1.126.0+bob2.3.0.20261026121409`).

1. "Would this be auto-approved?" / "why did it prompt?" →
   `python3 "<skill-dir>/scripts/approval_check.py" "<command>"` (`--settings PATH`, `--workspace DIR`,
   `--approved PAT`, `--denied PAT`). It runs the exact token matcher and the always-on regex heuristics, and
   approximates the 2.3.0 gate that flags a command writing to a path covered by `.bobignore` (or `.gitignore`
   when `session.respectGitIgnore` is on) from the files of `--workspace`; it cannot run the model check and it
   approximates the command split.
2. "How does it work?" / "is there a yolo mode?" → read `reference/approvals.md`: where a tool call is decided
   (PreToolUse hook, security check, approval flow), matching (token prefix, case-sensitive, no wildcards, longest
   pattern wins, tie → allow), the security check (heuristics → ignored-path write → setting → model, fail-closed;
   approved lists never bypass it), why there is no yolo mode in the IDE and what the most permissive settings
   still prompt for, folder trust (what is undetermined), enforcement.
3. Ground answers in the user's settings (`~/.bob/settings/settings.json`, workspace
   `.bob/settings.json`) and in `bob-telemetry security` for what was actually flagged.

Never suggest editing `extension.js`; never call `isCommandSecurityEnabled: false` harmless (it leaves the
heuristics and the ignored-path write gate, but removes the model check). Never present the Bob Shell "Safe mode"
or `--yolo` texts as IDE behaviour.
