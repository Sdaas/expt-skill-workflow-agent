# RESUME — shippable-plugin refactor

> Transient resume aid (like `REFACTOR-PLAN.md`; both are deleted at merge — Phase 5).
> The authoritative state is **`REFACTOR-PLAN.md` §0 + §5**. This file just holds a
> paste-ready prompt and the environment steps.

## Paste this into a fresh Claude Code session

```
Read REFACTOR-PLAN.md (on branch refactor/shippable-plugin) — §0 CURRENT STATE and §5
tell you where we are — and recall the project memories. We are POST Phase 2 (ii): Phase 1
(all 9 pile-1 fixes) is done, and BOTH minimal dry runs ran green — parse_duration (first)
and slugify (ii, confirming). This session's fixes are already committed: reviewer gates
pinned to claude-opus-4-8; exception-message test-quality shifted left of the mutation gate;
Gate 11 report persisted via analyzer --out; and the heredoc parser bug fixed in guard +
analyzer. The plugin loads from the WORKSPACE (not the cache) — no rsync needed, just a
session restart to pick up SKILL/agent edits. Do NOT revert to the old paced-tutorial
workflow. Commit per logical unit; update §5 as you go.

Plan: do Phase 4 first, then Phase 3.
- Phase 4 — the file-I/O + async-REST feature + fault-injection dry run. The container
  fixture ~/test-implement-feature is already scaffolded for it (webcache pkg, httpx,
  asyncio_mode=auto, workspace read-glob in .claude/settings.json). I (the user) drive the
  interactive /implement-feature in a container terminal; you analyze the run-log +
  transcripts and fix fallout on the branch. Two green dry runs = done.
- Phase 3 — docs: README router + docs/user-guide.md + developer-guide.md + tutorial.md,
  absorbing PATTERNS/TUTORIAL/LAUNCHING-SUBAGENTS/isolation-experiments per the §3 doc-fate map.

Confirm the environment is ready (Docker + container up; fixture present; host test venv),
then tell me the exact steps to drive the Phase 4 dry run.
```

## Environment for a Phase 4 dry run

The login lives in the named volume `expt-skill-workflow-claude`. The plugin loads
**directly from the workspace** (directory-source marketplace) — the `~/.claude/plugins/cache`
copy is **vestigial**, so there is **NO cache-sync step**. A workspace edit takes effect after
a **session restart** (SKILL/agents load at startup; the `guard.py` hook reloads per tool call).

1. `cd /Users/sdaas/dev/expt-skill-workflow-agent`
2. `devcontainer up --workspace-folder .` — idempotent; rebuilds the image only if missing
   (postCreate reinstalls the pinned toolchain).
3. **Start a FRESH container Claude session** so this session's committed plugin fixes load:
   `devcontainer exec --workspace-folder . bash` then inside: `cd ~/test-implement-feature && claude`
4. **Fixture** (Phase 4 = `~/test-implement-feature`): already scaffolded for the async-REST
   feature (`webcache` pkg, `httpx`, `asyncio_mode=auto`, `git init` on `master` so #8 forces a
   feature branch, and `.claude/settings.json` carrying BOTH read-globs — the workspace one is
   the load-bearing one in-container). If the container was rebuilt (`docker rm`) the fixture is
   gone — ask and it will be regenerated (see `phase2-dryrun-mechanics` memory).
   - For a maximally deterministic run, prefer destroying + rebuilding the container while
     KEEPING the volume (the login) — this is issue #21 (a v1.1 script; do it by hand for now).

## Analyzer over a run
```
devcontainer exec --workspace-folder . bash -lc '
  cd ~/test-implement-feature
  PYTHONPATH=/workspaces/expt-skill-workflow-agent/implement-feature-plugin \
    python3 -m analyzer.analyze_run --workdir ~/test-implement-feature/.implement-feature/<run>/'
```
(`--no-transcript` = fast isolation-only pass; `--out PATH` also saves the report — Gate 11
writes `<artifact_dir>/run-report.md`.) Run with cwd = the fixture dir so the transcript slug resolves.

## Host unit-test harness
`/tmp` is volatile — recreate:
`python3 -m venv /tmp/if-venv.tmp && /tmp/if-venv.tmp/bin/pip install pytest`, then
`/tmp/if-venv.tmp/bin/python -m pytest implement-feature-plugin -q` (expect **65** passing).
Full toolchain (ruff/mypy/mutmut) only runs in-container.
