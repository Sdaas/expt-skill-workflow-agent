# PATTERNS — Design Patterns, Anti-Patterns & Traps Checklist

> A running checklist we will apply when building both the toy example and the final
> `/implement-feature` solution. Updated as the tutorial reveals new patterns.
> ✅ = do this · ❌ = avoid this · ⚠️ = trap/tip to remember

---

## Skills
- ✅ **P1 — Trigger-oriented description.** Write a skill's `description` about *WHEN* to use it
  (situations, phrasings, triggers), not merely what it is. This is what decides activation.
- ✅ **P2 — Progressive disclosure.** Keep only lightweight name+description resident; put heavy
  detail in the body and in extra files loaded on demand. Skills can be long yet cheap.
- ❌ **A1 — Vague "what it is" description.** Leads to the skill firing at the wrong time (or never).

## Subagents & context
- ✅ **P3 — Context-as-files handoff.** Each phase writes a durable artifact file (spec, tests,
  review notes). Pass *filenames* to the next subagent: "do X; read f1, f2 for context."
  Files are durable, shared, single-source-of-truth, and survive across sessions.
- ✅ **P4 — Delegate heavy, self-contained jobs.** Hand context-heavy phases (write tests, deep
  review, mutation testing) to subagents so the orchestrator stays lean and focused on
  sequencing + talking to the user.
- ✅ **P5 — Crisp, self-sufficient briefs.** A subagent starts with a clean context; give it
  everything it needs in the brief (or via the files it should read).
- ❌ **A2 — Stuffing all context into the prompt** instead of files → drift, not reusable/durable.
- ❌ **A3 — Orchestrator doing context-heavy work inline** → context bloat, loss of focus.
- ⚠️ **T1 — Subagents have no memory of your conversation.** They see only what you pass. If it
  matters, write it to a file or put it in the brief.
- ⚠️ **T2 — Files prevent subagent drift.** All subagents reading the same artifact stay consistent.

---

## Workflow & gates
- ✅ **P6 — Driverless workflow = skill body as an ordered English script.** The agent is the
  runtime; numbered phases + gates + "repeat until" loops replace hand-written orchestration code.
- ✅ **P7 — Human-approval gates at control points.** "STOP. Do not continue until the user replies
  APPROVED." Use at: requirements clarity, spec sign-off, final review before commit.
- ✅ **P8 — Condition gates inside automated loops.** "Do not exit until all tests pass / mutation
  score ≥ threshold." The machine-checkable condition is the approver; no human needed → the loop
  grinds unattended until genuinely done.
- ✅ **P9 — Gate = approval checkpoint (not a frequency mechanism).** Approver is either a human or
  an automation. Choose per phase where the user wants control vs. where the machine should run free.
- ⚠️ **T3 — Prose gates are only as strong as their wording.** Weak: "ask the user." Strong:
  "**STOP. Do not write any code until the user replies APPROVED.**" Use imperative, unambiguous,
  capitalized stop-words.

## Testing & dev environment
- ✅ **P10 — Test workflow plugins in a disposable container sandbox.** Run Claude Code inside a dev
  container with its own isolated `~/.claude`; install/test the plugin there. Zero host footprint;
  throw the container away to reset. **Mandatory** for workflows that write files or commit code
  (e.g. `/implement-feature`) — it bounds the blast radius.
- ⚠️ **T4 — "Install" = config entry + cached copy.** `/plugin install` both records an entry in a
  settings file (`enabledPlugins`) AND materializes a cached copy under `~/.claude/plugins`.
  Project-scoped settings localize the *config entry* but NOT the cached copy — only a separate
  environment (container / different machine/user) fully isolates the host.
- ⚠️ **T5 — Keep plugin source separate from the installed copy.** Author + version-control in your
  repo; install *from* it (via a local marketplace). Never hand-edit the installed/cached copy —
  reinstalls overwrite it and it isn't tracked.
- ⚠️ **T6 — Container auth:** interactive Claude login works inside a container (CLI prints an OAuth
  URL you open on the host). Persist the container's `~/.claude` on a named volume so login survives
  restarts without re-authenticating.

- ✅ **P11 — Manage the sandbox with the `devcontainer` CLI + features (not hand-installs).** Declare
  tools (Node, Claude Code) as devcontainer **features** so they survive rebuilds; drive it with
  `devcontainer up/exec` (one config also works in VS Code). Put `.devcontainer/` at the **repo root**
  so the whole repo is the workspace. Avoids the "node without npm" build failure and keeps the
  toolchain pinned/reproducible.
- ⚠️ **T7 — Declare feature dependencies explicitly.** The Claude Code feature needs npm; add the
  Node feature *before* it, or the image build fails.

<!-- New patterns appended below as chunks reveal them. -->
