# Changelog

## 0.2 — unreleased

Two more Bob behaviours you can now explain and stop.

- **Understand why skills appear in `.bob/skills/` on their own.** Ask Bob why skills you never
  created keep coming back after you delete them, and it now has the answer — and it is not `/init`.
- **Stop them coming back.** Ask for a permanent fix and Bob applies one you can commit, so the
  skills stay gone for your whole team.
- **Get a Backlog task when you ask for a task.** Ask why Bob starts a subtask instead of creating
  a tracker task and it explains the mix-up; ask it to stop and it writes the rule that makes
  "task" mean your tracker again.

## 0.1 — 2026-09-08

First release. Five skills that answer questions about Bob from inside Bob.

- **Know which Bob you are running.** Version, build, the exact extension in use, whether Bob Shell
  is installed, and which models the server pushed to your machine today.
- **See what Bob costs you.** Bobcoins and tokens per task, per subagent and per call, split
  between the standard and the economy model — so an expensive habit becomes visible instead of
  showing up on the bill.
- **Understand approvals.** Why Bob asks you to confirm a command, whether a given command would be
  auto-approved before you run it, what the "Security warning" banner really means, and how to
  block a command for good.
- **See the rules Bob follows.** The instructions Bob gives itself about subagents, model choice
  and answering inline — read from the conversation Bob actually ran, not from a manual — and where
  your own `AGENTS.md` and `.bob/rules/` rank against them.
- **Make Bob follow your rules instead.** Always spawn a subagent when you ask for one, run
  subagents on the premium model, put your project workflow first, keep `/init` away from
  `AGENTS.md`, or refuse dangerous commands — Bob writes the right file in the right folder for you.
- **Trust the answers.** Every script checks the Bob version it is running against and warns you
  when your build is newer than the one these answers were verified on.
