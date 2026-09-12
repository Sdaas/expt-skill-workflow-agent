# RESUME — shippable-plugin refactor

> Transient resume aid (like `REFACTOR-PLAN.md`; **both are deleted in Phase 5 itself**).
> The authoritative state is **`REFACTOR-PLAN.md` §0 + §5**. This file just holds a
> paste-ready prompt and the environment steps.

## Where we are

Phases **0, 1, 2, 2(ii), 4, and 3** are all **DONE**. **Phase 5 (merge prep) is the only phase left.**
Phase 3 (docs) landed in 6 commits: the root `README.md` router, `docs/{user-guide,developer-guide,
tutorial}.md`, the transport-fault plugin nudge, and the doc-fate deletes (PATTERNS / TUTORIAL /
LAUNCHING-SUBAGENTS / PLAN / REVIEW-READING-ORDER / the whole `design/` dir, all absorbed into the DG
and Tutorial). Host unit tests: **65 green**.

## Paste this into a fresh Claude Code session

```
Read REFACTOR-PLAN.md (on branch refactor/shippable-plugin) — §0 CURRENT STATE and §5 tell you
where we are — and recall the project memories. All phases are done EXCEPT Phase 5 (merge prep).
Do the Phase 5 checklist in REFACTOR-PLAN.md §5, committing per logical unit. Do NOT revert to the
old paced-tutorial workflow. In order:

1. REWRITE CLAUDE.md. It still opens with a "⚠️ this repo is mid-refactor" banner and a
   "Resuming a session" block that points at REFACTOR-PLAN.md/RESUME.md — remove those. Keep the
   accurate, durable content (what the repo is; the conductor + isolated-gates architecture; the
   guard hook; quality standards/toolchain; the dev-container test harness; working conventions).
   It must read as the steady-state guide for a SHIPPED repo, not a refactor-in-progress. The docs/
   now hold the audience-facing detail — CLAUDE.md should point at them, not duplicate them.

2. NAME THE MARKETPLACE PROPERLY. .claude-plugin/marketplace.json is still named
   "toy-local-marketplace" (a tutorial leftover). Rename it to a real name (ASK the user which, or
   propose one like "daas-plugins"), then update EVERY reference:
     - docs/user-guide.md — the `claude plugin install implement-feature@<name>` commands AND the
       "Note on the marketplace name" paragraph (which can be deleted once the name is real), plus
       the uninstall command in the FAQ.
     - docs/tutorial.md — the toy-greet install walkthrough (`install toy-greet@<name>`).
     - DEVCONTAINER.md — the "enabled plugins/marketplaces" note (§ Claude Code UX).
     - .devcontainer/claude/settings.json (or wherever the dry-run fixture enables marketplaces) if
       it hardcodes the old name.
   Grep the repo for `toy-local-marketplace` to be sure nothing is missed.

3. FINAL README.md PASS — re-read against the final tree; fix anything stale.

4. VERIFY INSTALL-FROM-GITHUB FOR REAL (open risk, §6) — in a clean container: marketplace add from
   the GitHub repo, then install implement-feature@<new-name>, and confirm the User Guide's
   documented flow actually works end-to-end (this hits the ~/.claude/plugins cache path, unlike our
   workspace-source dry runs).

5. CLOSE ADDRESSED ISSUES with commit references, then DELETE the transient files
   (REFACTOR-PLAN.md AND RESUME.md), and MERGE refactor/shippable-plugin → main.
```

## Environment — dev container (rebuild only if you need step 4)

The plugin is never installed into the Mac's global `~/.claude`; for our testing it runs inside a dev
container with its own isolated `~/.claude` (login persisted in the named volume
`expt-skill-workflow-claude`). Steps 1–3 + 5 are pure repo edits on the Mac and need no container. Only
step 4 (real install-from-GitHub verification) needs a running container.

1. `cd /Users/sdaas/dev/sdlc-lite`
2. `docker ps -a | grep expt` (or `devcontainer up --workspace-folder .` — idempotent, rebuilds only
   if the container is gone or `.devcontainer/*` changed).
3. Shell in: `devcontainer exec --workspace-folder . bash`; or jump straight into Claude Code inside:
   `devcontainer exec --workspace-folder . claude`.
4. Note the plugin loads **from the workspace** (`/workspaces/sdlc-lite/
   implement-feature-plugin/**`), not the vestigial `~/.claude/plugins/cache` copy — so a workspace
   edit takes effect after a **fresh container Claude session restart**, with **no cache-sync step**.
   BUT step 4's real install-from-GitHub verification deliberately exercises the *cache* path (that's
   what a real end user hits), so do it as a fresh `marketplace add <github repo>` + `install`, not
   against the workspace source.

## Host unit-test harness (steps 1–3 don't change code, but handy)
`/tmp` is volatile — recreate:
`python3 -m venv /tmp/if-venv.tmp && /tmp/if-venv.tmp/bin/pip install pytest`, then
`/tmp/if-venv.tmp/bin/python -m pytest implement-feature-plugin -q` (expect **65** passing).
Full toolchain (ruff/mypy/mutmut) only runs in-container.

## Analyzer over a run (reference; not needed for Phase 5 unless re-verifying a dry run)
```
devcontainer exec --workspace-folder . bash -lc '
  cd ~/test-implement-feature
  PYTHONPATH=/workspaces/sdlc-lite/implement-feature-plugin \
    python3 -m analyzer.analyze_run --workdir ~/test-implement-feature/.implement-feature/<run>/'
```
(`--no-transcript` = fast isolation-only pass; `--out PATH` also saves the report — Gate 11 writes
`<artifact_dir>/run-report.md`.) Run with cwd = the fixture dir so the transcript slug resolves.
