# RESUME — shippable-plugin refactor

> Transient resume aid (like `REFACTOR-PLAN.md`; both are deleted at merge — Phase 5).
> The authoritative state is **`REFACTOR-PLAN.md` §0 + §5**. This file just holds a
> paste-ready prompt and the environment-rebuild steps.

## Paste this into a fresh Claude Code session

```
Read REFACTOR-PLAN.md (on branch refactor/shippable-plugin) — §0 CURRENT STATE and §5
tell you where we are — and recall the project memories. We are POST Phase 2 first dry
run: Phase 1 (all 9 pile-1 fixes) is done, and the parse_duration dry run ran green
end-to-end with all invariants holding; five triage items already landed (two guard
false-positives, P56 conductor-model self-check, gitignore the if-runlog fallback, P57
smallest-viable scope anchor). Do NOT revert to the old paced-tutorial workflow. Commit
per logical unit; update §5 as you go.

Pick the next step and tell me your recommendation first:
(i)  Phase 3 — docs: README router + docs/user-guide.md + developer-guide.md + tutorial.md,
     absorbing PATTERNS/TUTORIAL/LAUNCHING-SUBAGENTS/isolation-experiments per the §3 doc-fate map;
(ii) a quick SECOND minimal dry run to confirm P57 (scope anchor) + P56 (model self-check)
     actually change conductor behavior before the big feature;
(iii) Phase 4 — the file-I/O + async-REST feature + fault-injection dry run.
```

## Rebuilding the container (you deleted the container AND the image; the volume was kept)

The login + the plugin cache with the Phase-1 code live in the named volume
`expt-skill-workflow-claude`, which you did **not** delete — so they persist. Only the
container/image and the fixture repo are gone.

1. `cd /Users/sdaas/dev/expt-skill-workflow-agent`
2. `devcontainer up --workspace-folder .` — **rebuilds the image** this time (slower;
   postCreate reinstalls the pinned toolchain), then starts the container.
3. `devcontainer exec --workspace-folder . claude` — login should persist via the volume.
4. **Re-sync the plugin cache to the branch** (the container runs a hard-synced cache, and
   after any plugin edit it must be refreshed — see the `phase2-dryrun-mechanics` memory):
   ```
   devcontainer exec --workspace-folder . bash -lc '
     C=/home/vscode/.claude/plugins/cache/toy-local-marketplace/implement-feature/0.1.0
     rsync -a --delete --exclude __pycache__ --exclude ".*_cache" \
       /workspaces/expt-skill-workflow-agent/implement-feature-plugin/ "$C"/'
   ```
   (Restart any running `claude` session afterward — SKILL/agents load at startup; the
   guard hook reloads per tool call.)
5. **Recreate the dry-run fixture** (it lived in the container home, not the volume, so it's
   gone). Rebuild `~/test-implement-feature`: a `pyproject.toml` (src-layout), empty
   `src/durations/` + `tests/`, a `.claude/settings.json` with the plugin read-allow rule,
   and `git init` (its default branch triggers #8's feature-branch requirement). The scaffold
   is described in the `phase2-dryrun-mechanics` memory; ask me and I'll regenerate it.

## Host unit-test harness
`/tmp` is volatile — recreate:
`python3 -m venv /tmp/if-venv.tmp && /tmp/if-venv.tmp/bin/pip install pytest`, then
`/tmp/if-venv.tmp/bin/python -m pytest implement-feature-plugin -q` (expect 58 passing).
Full toolchain (ruff/mypy/mutmut) only runs in-container.
