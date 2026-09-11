# RESUME — shippable-plugin refactor

> Transient resume aid (like `REFACTOR-PLAN.md`; both are deleted at merge — Phase 5).
> The authoritative state is **`REFACTOR-PLAN.md` §0 + §5**. This file just holds a
> paste-ready prompt and the environment steps.

## Paste this into a fresh Claude Code session

```
Read REFACTOR-PLAN.md (on branch refactor/shippable-plugin) — §0 CURRENT STATE and §5 tell
you where we are — and recall the project memories. Phases 0–2(ii) are done. Phase 4 was
started (not Phase 3): the async cached JSON fetcher feature (`CachedFetcher`) ran end-to-end
through all gates in the container and landed a real commit (`7047829`) on
`feature/00-async-cached-json-fetcher`. Three fixes are already committed on this branch: the
Gate 0 STOP-summary restyle, a non-importable-package preflight/RED-classification fix, and a
container UX provisioning commit, plus a corrected Gate 0 note about reviewer model pinning.
Do NOT revert to the old paced-tutorial workflow. Commit per logical unit; update §5 as you go.

ONE thing is open before Phase 4 can be called done:

1. ✅ DONE — model-pinning re-audit. Settled from raw transcripts across all four sessions:
   the dated `claude-opus-4-8` reviewer pin **IS honored** in every post-pin session (incl. the
   committed Phase 4 run, session `251d3474`). The earlier "not honored" claim misattributed a
   Sep-10 pre-pin `parse_duration` session to Phase 4. `design/model-pinning-findings.md` is
   closed; the Gate 0 SKILL.md note (`133025c`) was confirmed correct as written.
2. **Run the fault-injection pass** (network timeouts, 5xx responses) against the async fetcher
   feature — the second half of Phase 4's done-bar (the un-mocked VERIFY gate, the resiliency
   review dimension, and the concurrency policy need to be genuinely exercised, not just
   asserted). **Mechanism decided: `httpx.MockTransport`** (deterministic, no network / no extra
   process, fits the pinned toolchain).

Only after the fault-injection pass lands does Phase 4 count as done — then move to Phase 3
(docs: README router + user-guide.md + developer-guide.md + tutorial.md, absorbing
PATTERNS/TUTORIAL/LAUNCHING-SUBAGENTS per the §3 doc-fate map).
```

## Environment — container is already up and populated, no re-bootstrap needed

The login lives in the named volume `expt-skill-workflow-claude`. The container
(`vibrant_kapitsa` as of 2026-09-11) was left **running**, with the fixture already scaffolded
and the Phase 4 run's artifacts intact — do **not** tear it down or re-bootstrap the fixture
before checking what's there.

1. `cd /Users/sdaas/dev/expt-skill-workflow-agent`
2. Check the container is still up: `docker ps -a | grep expt` (or `devcontainer up
   --workspace-folder .` — idempotent, only rebuilds if the container is actually gone).
3. Shell in: `devcontainer exec --workspace-folder . bash` (or `docker exec -it <name> bash`),
   then `cd ~/test-implement-feature`.
4. `git log --oneline -3` should show `7047829 Add async cached JSON fetcher (CachedFetcher)...`
   on `feature/00-async-cached-json-fetcher`. `git diff --stat` shows ~3 lines of uncommitted
   local drift in `.claude/settings.json`/`.gitignore` from the run — harmless, review before
   continuing.
5. The plugin loads **directly from the workspace** (directory-source marketplace) — the
   `~/.claude/plugins/cache` copy is **vestigial**, so there is **no cache-sync step**. A
   workspace edit (e.g. from step 1 above) takes effect after a **fresh container Claude
   session restart** (SKILL/agents load at startup; the `guard.py` hook reloads per tool call).
6. The run's handoff + transcripts are still on disk:
   `~/test-implement-feature/.implement-feature/00-async-cached-json-fetcher-202609110808/` and
   `~/.claude/projects/-home-vscode-test-implement-feature/251d3474-c0c0-4d49-b39e-34af100f71ff*`
   — use these for the model-pinning re-audit (step 1 of the resume prompt above) before
   starting anything new.

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
