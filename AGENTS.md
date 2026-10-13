# Agent instructions

The working rules for this repository live in **[`CLAUDE.md`](CLAUDE.md)**. Read that
file first, whichever agent you are.

It is kept deliberately short — about one screen — because long rule files get
skimmed. The reasoning behind each rule lives in [`MISTAKES.md`](MISTAKES.md).

## The two-minute version

- Static HTML/CSS/JS marketing site. **No framework, no build step, no npm
  dependencies.** There is no `package.json` and the audit fails if one appears.
- Hungarian is the source language. `site/en/index.html` is **generated** by
  `scripts/build-en.py` — never edit it by hand.
- Two test layers, both must pass before a commit:

```bash
python3 tests/audit.py            # 85 checks, no dependencies, in the pre-commit hook
python3 tests/render-check.py     # 62 checks in a real browser (needs playwright)
```

- Secrets are scanned by both the pre-commit hook and the audit, **with no file
  exclusions**. Do not add one.
- `.github/workflows/*` cannot be pushed by the usual token — workflow changes go
  through the GitHub web editor.

Everything else, including the rules that are not obvious, is in `CLAUDE.md`.
