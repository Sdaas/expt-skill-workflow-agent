# Isolation & subagent-mechanics experiments (Chunk 13 deviation)

> **Date:** 2026-09-07. **Question:** can we actually launch a subagent with a chosen
> model, effort, and allowed/disallowed tools, and confine + prove which files it reads —
> before building the rest of `/implement-feature` on that assumption?
> **Verdict:** yes, with caveats. Model + tool-restriction + read-audit are proven; hard
> read-confinement is achievable via a working-directory fence; project hooks and effort
> need care. Details below.

## Method
- **Stage 0:** authoritative docs via the `claude-code-guide` agent.
- **Stage 1 (host session):** spawned trial subagents via the Agent tool; verified ground
  truth by parsing each subagent's JSONL transcript (`tasks/<id>.output`) with a prototype
  analyzer (a throwaway session-scratchpad script, not retained) — never trusting self-report.
- **Sandbox (dev container, headless `claude -p`):** installed the real plugin; tested
  plugin-agent discovery and read-confinement mechanisms.

## Results

| # | Experiment | Result |
|---|------------|--------|
| E1 | Model routing (Agent-tool `model` override) | ✅ **Honored & transcript-provable.** haiku→`claude-haiku-4-5-20251001`, sonnet→`claude-sonnet-5`. No override → inherits parent (opus). |
| E2 | Tool restriction (`tools`/`disallowedTools`) | ✅ **Hard block.** The read-only Explore agent had **no Write tool at all**; general-purpose (all tools) could write. |
| E3 | Read audit (transcript parse) | ✅ **Works.** The analyzer recovers each subagent's exact `Read`/`Bash` targets + per-agent model + token usage from its transcript. |
| E5 | Plugin-agent discovery + naming | ✅ Discoverable after install, but **NAMESPACED**: `implement-feature:test-writer` (not bare `test-writer`). Fixed in `SKILL.md`. |
| E6a | Confinement via **project PreToolUse hook** | ❌ **Did not fire** in headless `claude -p` (canary leaked, audit log empty). Project-dir hooks appear to need trust / user-scope. |
| E6b | Confinement via **`blockReadsOutsideWorkingDirectories`** | ✅ **Hard-blocks both `Read` and Bash `cat`** of a path outside the working dir, in headless mode. |

### Stage-0 facts (docs)
- `tools` / `disallowedTools`: **enforced** hard restrictions.
- `effort`: pinned **only** via agent-def frontmatter (key = `effort`); **no** inline
  spawn-time override (model *can* be overridden inline). Not easily observable — trusted,
  not yet empirically confirmed to change behavior.
- Plugin agents auto-discover when enabled; **namespaced** (confirmed by E5).
- **No per-path read-deny setting.** Options: `blockReadsOutsideWorkingDirectories`
  (all-or-nothing fence, confirmed working) or a PreToolUse hook (fine-grained, but see E6a).
- `isolation: worktree` = full-repo copy; **does not hide a specific file**.
- Transcript JSONL parsing **works today** but the format is officially internal/unstable —
  treat the analyzer as best-effort, cross-checkable, not a supported API.

### Side findings
- Project `.claude/agents/` load in a **fresh** session but do **not hot-reload** mid-session
  (host spawn of a just-created def failed; a fresh container session saw it).

## Recommended isolation posture (for the algorithm-blind test-writer)
**Hard confinement, proven path:** stage the test-writer's inbox (`requirements.md`,
`design-interface.md`, `test-plan.md`) *inside* its working directory; keep
`design-internal.md` **outside** that directory; run under
`permissions.blockReadsOutsideWorkingDirectories: true`. Then Read *and* Bash are both
fenced off the algorithm. (Optionally combine with `isolation: worktree` for the working
dir, keeping the secret out of the repo/worktree.)
**Detective audit for all gates:** the transcript analyzer (proven) as best-effort
observability; revisit a user-scope hook for a supported audit log later.

### DECISION (2026-09-07)
Adopt the **most rigorous** posture: **hard-confine the test-writer AND build a supported
audit hook now**. After research + a second round of experiments, the chosen mechanism is
a **plugin-shipped PreToolUse hook** (`implement-feature-plugin/hooks/hooks.json` →
`hooks/scripts/guard.py`) — it turned out to do all three jobs in one place, so the
working-dir fence is unnecessary (kept only as optional defense-in-depth).

### Hook experiments (round 2) — the guard hook is VALIDATED
Setup: shipped the hook with the plugin; reinstalled in the container; drove headless.

| # | Test | Result |
|---|------|--------|
| H1 | Plugin hook fires in headless, for main session | ✅ run-log written |
| H2 | Read `.env` (any agent) | ✅ **DENIED** live ("reading secrets/.env is not allowed") |
| H3 | Plugin hook fires for a **subagent**, with `agent_type` | ✅ logged `agent_type=implement-feature:test-reviewer` + `agent_id` |
| H4 | test-reviewer reads `design-internal.md` | ✅ **allowed** (only test-writer is blind) |
| H5 | test-writer asked to read `design-internal.md` | ✅ **refused on its own role instructions** before the hook even fired (defense-in-depth) |
| U(A–F) | `guard.py` unit tests (crafted stdin) | ✅ all pass: deny test-writer+design-internal (Read & Bash), allow reviewer, deny .env/ssh-keys for all, allow normal, log every call |

**Confirmed facts (empirical, correcting the docs where they differed):**
- **Plugin** PreToolUse hooks DO fire in headless — including for subagent tool calls —
  whereas a **project `.claude/settings.json`** hook did NOT (E6a). Ship the hook *with the
  plugin*.
- The PreToolUse stdin includes **`agent_type`** (namespaced, e.g.
  `implement-feature:test-writer`) and **`agent_id`** — enough to enforce per-agent rules
  and attribute every read in the run-log.
- `deny` + exit code 2 hard-blocks the tool call.

### Final posture (implemented)
1. **Guard hook** (plugin PreToolUse) = the primary mechanism: (a) audit every tool call to
   the run-log; (b) deny secrets/`.env`/keys for ALL agents (reusable security guardrail);
   (c) deny `design-internal.md` for the test-writer (algorithm-blind), Read *and* Bash;
   (d) deny Edit/Write to test files for the implementer (test-integrity — added Chunk 15).
2. **Role discipline** in the agent-def bodies stays (defense-in-depth; it stopped the read
   before the hook in H5).
3. **Observability analyzer:** the hook run-log is the stable audit source. A transcript
   parser is still needed as a best-effort source for per-agent **model + token** figures
   (not covered by the run-log); the Stage 1 prototype was a throwaway and was not retained.
   To be built and committed into the plugin at the observability chunk (see issue #4).
4. Working-dir fence (`blockReadsOutsideWorkingDirectories`) / `isolation: worktree`:
   available as optional extra hardening; not required given the hook.

## Design changes triggered
1. `SKILL.md`: spawn agents by **namespaced** `subagent_type` (`implement-feature:<agent>`).
2. Workdir layout must place `design-internal.md` **outside** the test-writer's fenced
   working dir (to be wired when Gate 3 is run for real). Everything else stays in `handoff/`.
3. Observability run-log: transcript-parse analyzer is feasible; a hook-based log needs
   user-scope/trust (deferred).

## Open (not blocking)
- E4 effort: confirm it actually changes behavior on a loaded plugin agent (low priority).
- A supported, trusted audit-hook configuration (user settings) for the run-log.
