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

## Installing & invoking plugins
- ✅ **P12 — Plugin commands are namespaced `/<plugin>:<command>`.** `commands/greet.md` in plugin
  `toy-greet` → `/toy-greet:greet`, never bare `/greet`. Prevents collisions across installed plugins.
- ⚠️ **T8 — Prefer the CLI installer for scripted/deterministic installs.** Typing `/plugin install
  X@Y` as a one-liner in a session may just open the manager UI and no-op (no confirmation). Use
  `claude plugin install X@Y` (CLI), then `/reload-plugins` to activate in the current session.
  Verify with `claude plugin list` / `claude plugin marketplace list`.
- ⚠️ **T9 — `marketplace add` ≠ `install`.** `add` registers a catalog (nothing installed yet);
  `install <plugin>@<marketplace>` materializes + activates one plugin from it.

---

## Conductor + isolated gates (Chunk 9 — the real product's architecture)
- ✅ **P13 — Conductor [C] + isolated subagents [I].** One interactive **conductor** holds the
  through-line and talks to the human; delegate the *bias-sensitive* gates (write-tests, reviews,
  verify) to **isolated subagents** with fresh context. The human is the continuity thread integrating
  independent specialists. Keep interview / classify-confirm / human-review on the conductor.
- ✅ **P14 — Curated inbox/outbox handoff contract.** Every isolated gate reads a *defined* set of
  files (its inbox) and writes a *defined* outbox — never the prior gate's raw transcript. Write the
  contract as an explicit table. Formalizes P3.
- ✅ **P15 — Algorithm-blind test-writer via interface/internal design split.** Split the design into
  `design-interface.md` (public contract, shared with the test-writer) and `design-internal.md`
  (algorithm, **withheld**). The test-writer sees requirements + interface ONLY, so its tests encode
  the *contract*, not the code — killing anchoring. (Validated in the `claude-sdlc` A/B.)
- ✅ **P16 — TEST-REVIEW gate, before implement.** After write-tests and *before* implement, a
  **fresh, different** subagent reviews the tests against requirements + full design: do they encode
  the ACs, are they non-tautological, do they cover the boundary inventory + mutation cases? Running
  it pre-implement keeps the intent-match pure and stops weak tests anchoring the implementation. This
  was isolation's standout win over single-session self-review.
- ✅ **P17 — Model plan at CLASSIFY + `review > implementation` invariant.** Gate 0 proposes a
  per-gate model/effort table; the human approves/adjusts before any work. Invariant: **design and
  every review use a higher model (or effort) than implementation** (e.g. Opus reviews, Sonnet
  implements). Pin BOTH model and effort via **agent-definition files** (`.claude/agents/*.md`
  frontmatter) — the Task tool can set model inline but not effort.
- ✅ **P18 — Capture technology/design constraints, not just behavior.** The interview must explicitly
  ask for mandated/forbidden tech, libraries, patterns, style ("use jdbc not spring") — a section
  distinct from functional and non-functional acceptance criteria.
- ✅ **P19 — Grilling-style interview: design tree, worked in rounds.** Model the interview as a tree
  of decisions; each round ask the whole *frontier* (questions whose prerequisites are settled), one
  numbered question at a time **with your recommended answer**, then wait. **Facts are the agent's
  job** (dispatch a sub-agent to look them up); **decisions are the user's**. Done when the frontier
  is empty. (Borrowed from the `grilling` skill.)
- ✅ **P20 — Observability: prove + measure the run.** Emit a live `run-log.jsonl` (declared
  agent/model/inbox per gate) AND parse the session transcript JSONL post-hoc for ground truth
  (model/tokens/tool-calls/files-read). Enforce isolation **preventively** (restrict tools/paths or
  `isolation: worktree`) **and** verify it **detectively** (audit files actually read vs the declared
  inbox). The analyzer is **deterministic Python** — measurement code, not orchestration, so it
  doesn't violate the driverless principle.
- ⚠️ **T10 — VERIFY ≠ green tests.** "Not Done on green tests alone." Drive the *real* function on
  each acceptance criterion and exercise every external boundary **un-mocked** at least once — a
  mocked test only proved the mock.
- ⚠️ **T11 — Bound every automated loop.** TEST-REVIEW and CODE-REVIEW loops must stop after N rounds
  with no progress and surface to the human, or they can grind forever on an intractable finding.
- ⚠️ **T12 — Standards live in skills, not briefs (single source of truth).** A subagent brief LOADS
  the quality standard (via `skills:` frontmatter / read-by-path); it does not restate it. To raise
  the bar, enrich the skill, not every brief.
- ⚠️ **T13 — Conductor can't read a subagent's internal token count** from the Task return value —
  the ground truth is the session transcript JSONL. Real *proof* means parsing the transcript, not
  trusting self-reports.

---

## Scaffolding & quality gating (Chunk 10)
- ✅ **P21 — Thin command, heavy skill.** A command file is loaded into context **always**
  (even when not invoked), so keep it near-empty — it just loads the skill. Put the heavy
  workflow prose in `SKILL.md`, which loads **on demand** (progressive disclosure, P2).
- ✅ **P22 — Pin the toolchain + hard-fail preflight.** Because the workflow is prescriptive
  about the dev container, declare the exact tools (`toolchain/requirements-dev.txt`), install
  them in the container (`postCreateCommand`), and **verify presence at Gate 0 — STOP if any tool
  is missing.** Freeze exact versions after the first clean install (reproducibility).
- ✅ **P23 — Split quality checks by speed.** Fast checks (lint `ruff` + types `mypy` + unit
  `pytest`) define the **inner-loop "green"** the implementer must reach; slow checks (coverage
  `pytest-cov` + mutation `mutmut`) gate **CODE-REVIEW**. Keeps the tight loop fast; the reviewer
  owns the deep, judgement-heavy checks.
- ✅ **P24 — Universal commands in one standards file; per-feature thresholds in the test plan.**
  Tool *invocations* + the Definition of Done live once in `references/quality-standards.md`
  (extends T12); the coverage/mutation *numbers* are per-feature and live in Gate 2's test plan.
- ✅ **P25 — Situational checks are boundary-driven, not always-on.** Concurrency testing is
  mandated by the test plan **only** when the boundary inventory shows the feature is
  concurrent/async; otherwise skip with a stated reason (same shape as a VERIFY skip, T10).
- ⚠️ **T14 — Read-only critics buy independence, not just safety.** `disallowedTools: Write, Edit`
  on the reviewer/verifier stops them *silently "fixing"* (and hiding) a problem, and keeping them
  as **separate** agents from the author stops self-review sharing the author's blind spots. The
  restriction enforces the independence that makes the critique real (P13/P16).
- ⚠️ **T15 — Plugin runtime-path & namespacing need verifying.** Whether plugin-provided **agents**
  auto-discover from `agents/`, how their names are addressed when spawned, whether `effort:` is
  honored for plugin agents, and how a subagent resolves a skill-relative file path — all confirmed
  at install-time in the sandbox, not assumed.

---

## Interview & handoff artifacts (Chunk 11)
- ✅ **P26 — Borrow the interview engine, but wrap it with schema + gate + handoff.** Reuse the
  `grilling` method (design tree, rounds, frontier, numbered Qs w/ recommended answers, facts-via-
  subagent), but bind it to a **required output schema** (the four buckets: functional ACs,
  non-functional ACs, constraints, boundary inventory), an **approval gate**, and a **durable outbox**.
  Frontier-empty is necessary but not sufficient — the schema must also be fully covered.
- ⚠️ **T16 — Write a handoff artifact only AFTER approval.** For a file downstream gates treat as a
  trusted contract, its *existence should equal its blessing*. Writing pre-approval risks an abandoned
  half-baked file and downstream gates ingesting un-approved content as truth. Summarize → APPROVED →
  write.
- ⚠️ **T17 — Force explicit "none" for enumerations.** Make "None (pure feature)" a required answer
  for the boundary inventory, so downstream gates can tell "no boundaries" apart from "forgot to list
  them" — the latter lets a real boundary go un-exercised (T10) and the defect escapes.

---

## Design / spec (Chunk 12)
- ✅ **P27 — Record rejected alternatives (ADR) in the durable design file.** `design-internal.md`
  captures the alternatives considered and *why they were rejected*, not just the chosen approach — so
  "why this and not that?" is answerable months later, and the reviewer can check the decision still
  holds. (Extends the interface/internal split, P15, and the file-handoff discipline, P3.)

<!-- New patterns appended below as chunks reveal them. -->
