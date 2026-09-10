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
  at install-time in the sandbox, not assumed. **RESOLVED (Chunk 13):** plugin agents auto-discover
  when installed and are addressed by the **namespaced** `subagent_type` `implement-feature:<agent>`
  (NOT bare); effort is a frontmatter-only pin. See `LAUNCHING-SUBAGENTS.md`.

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

---

## Launching & isolating subagents (Chunk 13 — validated; see `LAUNCHING-SUBAGENTS.md`)
- ✅ **P28 — Enforce isolation with a plugin PreToolUse guard hook.** Ship a hook
  (`hooks/hooks.json` → a script via `${CLAUDE_PLUGIN_ROOT}`) that does three jobs for the conductor
  AND every subagent: (a) **audit** every Read/Bash to a run-log, (b) **deny secrets/`.env`/keys** for
  all agents, (c) **deny a specific file for a specific role** by keying on the stdin `agent_type`
  (e.g. `design-internal.md` for the test-writer). A `deny` decision + exit 2 hard-blocks the call.
- ✅ **P29 — Defense-in-depth: role instruction + hook.** Keep the "do NOT read X" line in the agent's
  own brief AND the hook block. The agent usually declines on its own; the hook is the backstop if it
  doesn't. Two independent gates.
- ✅ **P30 — Ship reliability-critical config WITH the plugin, not project settings.** A project
  `.claude/settings.json` PreToolUse hook did NOT fire in headless `claude -p`; the **plugin** hook did
  (and for subagents). Put must-fire hooks in the plugin (or user settings).
- ✅ **P31 — Attribute every tool call via `agent_type`/`agent_id`.** The PreToolUse stdin carries the
  calling agent's namespaced type + id — enough for per-agent rules AND a trustworthy audit trail.
- ⚠️ **T18 — Effort is frontmatter-only.** No spawn-time override; pin `effort:` in the agent-def (else
  it inherits the parent). Model CAN be overridden inline; effort cannot.
- ⚠️ **T19 — Tool-deny ≠ read-confinement.** `disallowedTools: Write` stops writing, not reading. To
  confine reads use `blockReadsOutsideWorkingDirectories` (all-or-nothing fence) or the hook (P28).
- ⚠️ **T20 — `isolation: worktree` does not hide in-repo files.** It's a full branch copy; keep a file
  out of the agent's reach via the fence or the hook, not the worktree.
- ⚠️ **T21 — Verify runtime behavior; don't trust docs/config.** The docs guessed "bare name" for
  plugin agents (wrong — namespaced) and were unsure about headless hooks (project=no, plugin=yes).
  Confirm model, tool blocks, hook firing, and naming empirically before depending on them.

---

## Review gates (Chunk 14)
- ✅ **P32 — Asymmetric inboxes: blind the producer, inform the critic.** The producer that must stay
  unbiased (test-writer) gets a *restricted* inbox; the critic that judges it (test-reviewer) gets the
  *full* context (incl. `design-internal.md`) so it can catch what the producer couldn't. Same
  file-handoff machinery, opposite information policy — enforced per-agent by the guard hook (P31).
  A review gate also runs BEFORE the thing it protects (test-review before implement, P16) and its
  critic is a different, read-only, higher-model agent (P13/T14/P17), looped but bounded (T11).

---

## Implementation gate (Chunk 15)
- ✅ **P33 — Stop the producer from grading its own homework.** The implementer must make the code
  pass the tests, never edit the tests to pass. Enforce it the same way as algorithm-blindness: a guard
  hook that denies the implementer (`agent_type`) any Edit/Write to a **test file** — plus the prose
  rule and the whole-diff code-review (three layers). Generalizes: whenever an agent's *acceptance
  criteria* live in files it can technically edit, deny it write access to those files by role.

---

## Verification (Chunk 16)
- ✅ **P34 — Nested inner/outer loop: unit-green inside, observed-behavior outside.** The inner loop
  (IMPLEMENT) closes on machine-checkable unit green (pytest+ruff+mypy); the outer loop (VERIFY) closes
  only when the **real** feature is driven on each AC and every boundary is exercised **un-mocked** — a
  fresh, read-only agent, not the author. A defect in the outer loop re-enters the inner loop. "Green
  tests are not Done" (T10) is the reason the outer loop exists; independence (P13) is why a different
  agent runs it.

---

## Code review (Chunk 17)
- ✅ **P35 — Mutation kill-rate retroactively grades test quality.** A surviving mutant is a
  deliberately-injected bug no test caught → a weak/tautological test. Running mutation at CODE-REVIEW
  turns "are the tests any good?" into a machine-checkable number that retroactively grades the
  test-writer (Gate 3) and the test-reviewer (Gate 4) — the objective backstop behind the earlier
  human/agent judgement. Whole-diff review by one fresh, stronger, read-only agent (P13/P17/T14) is the
  last unattended gate before the human.

---

## Human hand-back (Chunk 18)
- ✅ **P36 — Bookend with human gates; keep the machine gates in the middle.** The human owns the
  *ship decision* (a machine can't be accountable), so a final STOP-until-APPROVED gate precedes the
  only git-writing step (review-before-commit is a hard rule, not a default — P7/T3). Make that review
  cheap for the human: a REVIEW-GUIDE gate that orders the changed files and points at every findings
  file + the run-log (the observability payoff). Mechanical gates (guide, commit) run on cheap models
  (Sonnet/Haiku); reserve the strong models for judgement (design/reviews).

## Code review — routing revision (Chunk 17 discussion, 2026-09-09)
- ✅ **P37 — Type each review finding by its repair actor; one review pass can fan out to
  several fix gates.** A whole-diff reviewer produces findings whose *corrections live in
  different places*: a correctness/best-practice/reliability defect is fixed in `src/`
  (→ IMPLEMENT), but a **surviving mutant or a missing-test coverage gap is a *test* weakness**
  — and the implementer is contractually barred from editing tests (guard-hook job #4), so
  routing it to IMPLEMENT is a **dead-end loop**. Fix: the reviewer TAGS every finding
  (`→IMPLEMENT` / `→TESTS`); the conductor routes each tag to the right gate (`→TESTS` re-enters
  **WRITE-TESTS then TEST-REVIEW**, because new tests must be independently reviewed before
  re-use). Keep it **one gate / one review pass** (efficiency: one fresh Opus context) but **two
  repair paths** — don't split into two phases just because the loops differ. Ambiguous case: a
  surviving mutant that is *unreachable-by-requirement code* is a code defect (→ IMPLEMENT to
  delete), not a test gap — so routing needs the reviewer's judgement, not a mechanical
  check-type map. Related: P34 (nested loops), P35 (mutation grades tests), P32 (asymmetric
  inboxes).
- ✅ **P38 — Borrow a review rubric from a fixed dimension set, and state N/A explicitly.** The
  CODE-REVIEW checklist now covers the six `claude-sdlc` quality dimensions (best practices,
  performance & scale, testing pyramid, security, reliability & resilience, observability &
  logging) instead of an ad-hoc list. A fixed set stops the reviewer from silently forgetting a
  dimension; **`N/A — why`** (never a dropped section) makes "doesn't apply here" a recorded
  decision, not an oversight. Our old list quietly omitted performance, reliability, and
  observability; "concurrency" was only a slice of reliability.

## Portability — a shipped workflow uses the ambient environment (Chunk 18 discussion, 2026-09-09)
- ✅ **P39 — A shipped workflow reads identity/config from the *ambient* environment; it never
  hardcodes the author's.** Gate 10 originally baked in `Soumendra Daas / soumendra.daas@gmail.com`
  as the commit author — fine for *this repo's own* commits (the `CLAUDE.md` meta-rule), but a
  **portability leak** in the *product*: a customer running the plugin would get commits attributed
  to the plugin's author. Fix: let `git commit` resolve `user.name`/`user.email` from ambient
  config (no `--author`, no `git config`); if none is set, **STOP and surface to the human** rather
  than inventing one; for a `Co-Authored-By:` trailer, follow the repo's existing convention.
  General rule: **separate meta-authorship (who builds the tool) from runtime behavior (what the
  tool does in someone else's environment)** — the tool inherits the host's identity, secrets,
  toolchain, and conventions, never the builder's.

## Observability — measurement, not orchestration (Chunk 19)
- ✅ **P40 — An observability layer must MEASURE, never ORCHESTRATE — so keep it deterministic code,
  not an agent.** The workflow's whole claim is "driverless" (no hand-written orchestration; behavior
  lives in Markdown). An after-the-fact analyzer is allowed to be real Python *only because* it reads
  logs and computes facts — it never calls a model, makes a decision, or drives a gate. Two reasons it
  must not be a summarizer subagent: **(1) trust** — "did the test-writer read the forbidden file?" is
  a grep-and-count fact; an LLM summarizer is non-deterministic and can *hallucinate a compliance pass*,
  while deterministic code is repeatable and auditable; **(2) architecture** — an analyzer *agent* is a
  second AI that *acts inside* the system, silently re-introducing a driver. Rule: **code is permitted
  when it measures (analyzer) or enforces (guard hook), never when it orchestrates.** It reads the two
  detective sources a run leaves — the guard hook's `if-runlog.jsonl` and the session transcript — and
  reports per-gate model/tokens/reads + an isolation-compliance pass/fail. Related: the guard hook
  (P28–P31) is the *preventive* twin; this is the *detective* twin.

## Building the analyzer (Chunk 20)
- ✅ **P41 — A monitoring/observability tool must FAIL LOUD, never silent.** For a tool whose only
  value is that you can *believe* it (P40), the cardinal sin is silent wrong/missing data — a
  clean-looking report that's actually hollow. Bias hard toward screaming on anything unexpected:
  route even *unknown* failures to the loud alarm (we `except Exception` on the transcript path and
  send it to the "format changed" message on purpose — ruff BLE001 suppressed with a rationale
  comment). Rationale = **asymmetry of errors**: a false-but-loud alarm is bounded, visible, and
  self-correcting; a silent gap is invisible and corrosive. Soften the blow, not the volume: hedge the
  wording ("*likely* changed") and always print the real exception as a diagnostic breadcrumb.
- ✅ **P42 — Quarantine an unstable dependency behind a boundary: stable core + best-effort satellite.**
  When one input is reliable (we own it) and another is officially unstable (someone else's format),
  split them into independent readers that never import each other, do the load-bearing work first, and
  wrap the fragile one in `try/except` at a single boundary. Degrade in **two clearly-distinguished
  modes**, because they mean different things and prompt different actions: **absent** (dependency not
  present — soft, expected note) vs **drift/broken** (present but unparseable — loud alarm, "update the
  parser"). Add a **schema self-check** that deliberately raises the loud error when the fields you
  depend on are gone — converting silently-wrong output into a loud failure. (Here: `runlog.py` is the
  core, `transcript.py` the satellite; a broken transcript can't dent the run-log report.)
- ✅ **P43 — Correlate two independent sources by a VALUE, not by coupling their code.** To keep the two
  readers decoupled, the only thing crossing the boundary is a **time window** (two datetimes) computed
  from the run-log and handed to the transcript reader — not a shared object, import, or mutable state.
  Correlation-by-value needs a **shared clock**: we fixed `guard.py` to log **UTC/tz-aware** so it lines
  up with the transcript's `Z` stamps, and the analyzer parses timestamps tolerantly (assume-UTC on
  naïve input; ±5-min pad) as a second line of defense. Selecting the transcript by *window overlap*
  (not "newest file") is robust to stray concurrent sessions.

- ✅ **P44 — `disallowedTools` is not a sandbox when `Bash` is granted.** Denying `Write`/`Edit` does
  **nothing** if the agent still has `Bash` — `cat >`, `echo >`, heredocs all write files. (Dry run:
  the "read-only" test-reviewer wrote both its report *and* `.py` files via Bash.) So a critic that
  needs Bash (to run pytest/ruff) can never be made read-only by tool-removal. Enforce the property you
  actually care about — *never mutates the product tree* — in the **guard hook** (deny writes whose
  visible target is under workdir `src/`·`tests/`); treat `disallowedTools` as documentation, not a
  fence. [#12, #16]
- ✅ **P45 — A critic may PROBE, never IMPLEMENT.** A reviewer may write **tiny throwaway probes** to
  answer a specific question (e.g. "does `int(float(bignum))` diverge?") but must not build a
  **reference implementation** of the feature under review. (Dry run: the test-reviewer built a full
  ref impl + ran 24 mutants.) Also: **mutation testing is implementation-specific** — mutants of a
  throwaway ref impl don't correspond to the shipped code's mutants, so empirical mutation belongs at
  the gate that has the *real* implementation (CODE-REVIEW), not before it. Pre-implementation review
  is **analytical** (name plausible bugs, confirm a test kills each). [#12, #13]
- ✅ **P46 — Anchored defaults beat free-pick.** An agent handed a metric with **no anchor** drifts (the
  design agent free-picked a 95% mutation kill-rate with no guidance). Ship a documented **default
  anchor** (80%) and require the agent to **justify deviations**, surfaced at the human approval gate.
  Per-feature flexibility (P24) + an anchor, not per-feature *arbitrariness*. [#13]
- ✅ **P47 — Never ask a human to approve an artifact they haven't seen in full.** Separate **authoring**
  (write the draft so the human reads the real thing) from **finalizing** (promote to the approved
  handoff downstream may consume). The old "don't write before approval" rule protected the handoff
  contract but blinded the reviewer. Fix: draft → **review the real file** → bounded revise loop
  (human hand-edits *and/or* agent revises; conductor re-reads disk as truth) → **promote** on approval.
  Uniform across every human STOP gate. [#11]
- ✅ **P48 — Separate PRODUCT from PROCESS artifacts by lifecycle.** Shipping code/config/tests belong in
  the repo's existing layout (feature-to-feature isolation is a **git branch** concern, not a
  filesystem one); process artifacts (design, findings, run-log) belong in a **per-run, gitignored
  workdir** (`.implement-feature/<NN-slug-timestamp>/`). Fusing them (workdir == repo root) collides the
  moment a second feature exists. [#10]
- ✅ **P49 — Pass per-run config to an out-of-band hook via a POINTER FILE, not env.** A hook is a
  separate process spawned by the platform; it does **not** inherit env a conductor exports in a tool
  call. To tell `guard.py` the current run's log path (decided at Gate 0, after launch), the conductor
  writes a fixed-path pointer (`.active-run`) the hook reads. The same file doubles as a **single-run
  lock** (fail fast if it exists). [#10]
- ✅ **P50 — Number handoff files in READ ORDER so the directory is self-documenting.** A human browsing
  `handoff/` should see the sequence in the file list itself (`01-requirements.md`,
  `02-design-interface.md`, …). Number by read-sequence (stable under loops: a re-review overwrites its
  numbered file). Safe because the guard matches by **substring**, so a numeric prefix still trips
  `design-internal`/test-integrity checks. [#17]
- ✅ **P51 — Observability must read where the PLATFORM actually writes — verify empirically.** The
  analyzer reported "subagents: none" because it read only the top-level transcript; Claude Code writes
  subagent transcripts under `<uuid>/subagents/*.jsonl` (+ `.meta.json`). The data proving model-pinning
  was there all along. Don't assume the log layout — inspect the real filesystem the platform produces.
  [#15]

- ✅ **P52 — Never commit on the default branch; assess triviality, recommend, but the guardrail
  is not overridable.** At Gate 0 the conductor assesses the feature's scope and *recommends* stay
  (trivial, non-default branch) vs a new `feature/<NN-slug>` branch — the branch name mirrors the
  run slug so branch↔artifacts correspond. The human may override the *triviality* judgment but
  **not** the hard invariant: a change is **never** committed on `main`/the default branch, so if
  HEAD is the default branch a new branch is *required* regardless of triviality. Enforced twice:
  the Gate 0 STOP-to-confirm and a re-check at Gate 10 before the commit lands. [#8]

<!-- New patterns appended below as chunks reveal them. -->
