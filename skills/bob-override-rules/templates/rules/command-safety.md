# Command safety at generation time

This workspace rule tells Bob what its own security check will refuse, so that such commands are
not proposed in the first place. It complements — it does not replace — the enforcing hook in
`.bob/hooks/command-guard.mjs`.

Before proposing any shell command, check it against these constraints. If it violates one, do
not run it: explain the step and ask the user to run it themselves.

- Never pipe remote content into an interpreter (`curl … | sh`, `wget … | bash`, `… | python`),
  never `eval` fetched or untrusted content, never decode base64 into a shell.
- Never put secrets on the command line (bearer tokens, passwords, API keys), and never read
  credential stores (`~/.ssh` private keys, `~/.aws`, `~/.bob/.env`, `/etc/shadow`) or grep for
  `*_token`, `*_secret`, `*_key`, `*_password` values.
- Never send local file contents to an external host (`curl -F "file=@…"`, `cat … | curl -X POST`,
  `nc`, `rclone`, `rsync` to third-party hosts).
- Never delete or overwrite outside the workspace; `rm -rf` only on named subdirectories of the
  workspace (`./build`, `node_modules`, `/tmp/...`).
- Never use `sudo` to modify system state, load kernel modules, or run `sudo` over SSH for writes.
- Never use obfuscating bash constructs: `${var@P}`, `${!name}`, escaped payloads inside `${…}`,
  here-strings fed by `$(…)`, extglob tricks.
- Keep commands short and single-purpose, with explicit paths; split long pipelines; no dynamic
  command construction.
- If a command was refused by the hook or flagged by Bob's security check, do not retry a
  variant: report what was attempted and ask.
