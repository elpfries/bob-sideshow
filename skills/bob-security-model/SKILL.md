---
name: bob-security-model
description: Use when the user asks why IBM Bob asks for approval, how approved or denied command patterns match (prefix, wildcard, case), what "Security warning" or requiresSecurityApproval means, how to set up auto-approve or a yolo-like mode, or whether a given command would be auto-approved.
---

# Bob security model

1. "Would this be auto-approved?" / "why did it prompt?" →
   `python3 "<skill-dir>/scripts/approval_check.py" "<command>"` (`--settings PATH`,
   `--approved PAT`, `--denied PAT`). It runs the exact token matcher and the always-on regex
   heuristics; it cannot run the model check and it approximates the command split.
2. "How does it work?" → read `reference/approvals.md`: matching (token prefix, case-sensitive,
   no wildcards, longest pattern wins, tie → allow), the security check (heuristics → setting →
   model, fail-closed; approved lists never bypass it), yolo, enforcement.
3. Ground answers in the user's settings (`~/.bob/settings/settings.json`, workspace
   `.bob/settings.json`) and in `bob-telemetry security` for what was actually flagged.

Never suggest editing `extension.js`; never call `isCommandSecurityEnabled: false` harmless.
