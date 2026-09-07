# TUTORIAL — Key Concepts, Commands & Takeaways

> A standalone study reference, appended after each chunk. Read top-to-bottom after the
> tutorial to review everything learned.

---

## Table of contents
- Chunk 1 — The four building blocks
- Chunk 2 — Anatomy of a skill
- Chunk 3 — Subagents
- Chunk 4 — The workflow pattern & gates
- Chunk 5 — Plugin packaging
- Q&A — The plugin.json manifest
- Chunk 6 — The toy build (`/greet`)
- Q&A — Where plugins install & the dev flow (host pollution)
- Decision — Dev-container test sandbox
- Chunk 7 — Building the sandbox (devcontainer CLI + features)
- Q&A — `devcontainer up` vs plain `docker run`
- Chunk 8 — Install & run the toy (marketplace → install → gates)
- Q&A — `marketplace add` vs `install`
- Correction — plugin commands are namespaced (`/plugin:command`)
- Chunk 9 — Designing `/implement-feature`: conductor + isolated gates
- Q&A — Borrow `grilling` vs delegate to it
- Q&A — Why per-gate models need agent-definition files
- Q&A — Proving isolation & tracking usage (observability)
- Chunk 10 — Scaffolding the conductor + agent-definition files
- Q&A — Where do lint/type/concurrency checks live, and how are tools guaranteed?
- Chunk 11 — Gate 1: the grilling-style INTERVIEW
- Q&A — Our Gate 1 vs the `grilling` skill
- Chunk 12 — Gate 2: DESIGN/SPEC + the interface/internal split + test plan
- Q&A — Why thresholds live in the test plan, and why record alternatives
- Chunk 13 — Gate 3: WRITE-TESTS + validating & enforcing subagent isolation
- Q&A — How is subagent isolation actually enforced (the guard hook)?

---

## Chunk 1 — The four building blocks

Four things nest together, smallest to biggest:

- **Skill** — a folder with `SKILL.md` (name + description + plain-English instructions). A
  reusable *instruction packet* / "playbook." Loads when its description matches the situation.
  Contains guidance, not running code.
- **Slash command** — a user-triggered entry point (`/implement-feature`). *You* press the
  button on purpose; commands are usually a thin file that says "run this workflow / load this skill."
- **Subagent** — a separate Claude instance given a focused job. Runs in its **own fresh context
  window**, does the work, returns only a result. Keeps the orchestrator's context clean; enables
  specialized, isolated work.
- **Plugin** — the distributable **package** bundling skills + commands + subagents + a manifest.
  How you install and share.

**Nesting:** plugin ⊃ (commands + skills + subagents); a command kicks off a skill; a skill may
delegate to subagents.

**Key distinction:** a *skill can auto-activate* by description; a *command is deliberate invocation*.

---

## Chunk 2 — Anatomy of a skill

A skill is a **folder** whose heart is `SKILL.md`, with two parts:

1. **Frontmatter** (YAML between `---` fences): `name` + `description`.
   - Claude reads *only name + description* to decide relevance.
   - `description` is the most important line: write it about **WHEN to use** (triggers,
     phrasings, situations), not just what it is. Bad description = skill fires at wrong times.
2. **Body** (Markdown below frontmatter): the actual instructions — steps, rules, gates, checklists.

**Progressive disclosure** (the key idea): Claude keeps only every skill's lightweight
`name` + `description` in context. The heavy **body loads on demand**, when the skill triggers.
→ Skills can hold long detailed instructions cheaply; they cost nothing until needed.

A skill folder can also ship **extra files** (templates, reference docs, scripts) referenced
from the body and loaded only when that step needs them — same disclosure principle, one level deeper.

Example frontmatter:
```yaml
---
name: implement-feature
description: Use when the user wants to build a new Python feature test-first...
---
```

---

## Chunk 3 — Subagents

A subagent is a **fresh Claude instance** the orchestrator spins up for one focused job.

1. **Isolated context.** Starts clean; sees only the brief + inputs you pass, not your whole
   conversation. You brief it explicitly.
2. **Does work, returns a result.** Runs its own tool calls in its **private context**, then
   hands back only a summary/result. Its intermediate churn never enters the orchestrator's context.
3. **Can be specialized.** Named subagent types with their own instructions and even restricted
   toolsets (e.g., a read-only reviewer).

**Why it matters here:** context-heavy, self-contained phases (write tests, deep review, mutation
testing) delegate cleanly, keeping the orchestrator focused on sequencing + talking to the user.

**Trade-off:** isolation means the subagent doesn't know what you discussed — pass everything it
needs (best via **context files**; see PATTERNS P3). Good delegation = crisp, self-sufficient brief.

---

## Chunk 4 — The workflow pattern & gates

A **workflow = a skill whose body is an ordered English script of steps and gates.** The **agent
is the runtime** — you don't write a loop that calls phase 1, phase 2; you write instructions the
agent executes conversationally. This is why "no driver code" is possible.

Three mechanisms:
1. **Sequenced steps** — numbered phases followed in order.
2. **Gates** — approval checkpoints that decide *whether* advancing is allowed.
3. **Loops-as-instructions** — "run tests; if any fail, fix and re-run; repeat until all pass."

**Gate = an approval mechanism, NOT a frequency mechanism.** The approver is either:
- **a human** — "STOP until the user replies APPROVED" (requirements, spec, final review), or
- **a machine-checkable condition** — "until all tests pass / mutation score ≥ threshold."

Our `/implement-feature` mixes both: human gates where the user wants control; condition gates
inside automated loops so the machine runs unattended until genuinely done.

**Subagents do the heavy sub-jobs; context files carry state; the skill body is the conductor's
score.** (Trap T3: word gates imperatively — "STOP. Do not… until APPROVED.")

---

## Chunk 5 — Plugin packaging

A plugin is a folder with a convention-based layout:

```
my-plugin/
├── .claude-plugin/plugin.json   ← manifest (identity metadata)
├── commands/    ← one .md per slash command (filename = command name)
├── skills/      ← one folder per skill (each has SKILL.md)
└── agents/      ← one .md per subagent definition
```

- The three content folders map exactly to Chunk 1's building blocks.
- Content is **auto-discovered by convention** — you drop a file in `commands/` and it just works;
  nothing is enumerated in the manifest. (Convention over configuration.)
- **Installation** wires everything in at once; plugins install from a **marketplace** (which can
  be a local folder or git repo with a `marketplace.json`).

---

## Q&A — The plugin.json manifest

**Q: What goes in the manifest, and what is each field?**

The manifest is **pure identity metadata** — it does NOT list your commands/skills/agents (those are
auto-discovered). Its presence in `.claude-plugin/` is what makes the folder a plugin.

```json
{
  "name": "implement-feature",
  "version": "0.1.0",
  "description": "Interview-driven, test-first workflow for building Python features.",
  "author": { "name": "Soumendra Daas", "email": "soumendra.daas@gmail.com", "url": "https://..." },
  "homepage": "https://...",
  "repository": "https://...",
  "license": "MIT",
  "keywords": ["tdd", "workflow", "python"]
}
```

| Field | Required | Purpose |
|---|---|---|
| `name` | **Yes** (only required field) | Unique kebab-case id; how the plugin is referenced. |
| `version` | Recommended | Semver `major.minor.patch`; lets a marketplace track updates. |
| `description` | Recommended | One-line summary in the plugin list. |
| `author` | Optional | Object (`name`, optional `email`, `url`) or a plain string. |
| `homepage` / `repository` | Optional | URLs to docs / source. |
| `license` | Optional | SPDX id (e.g. `MIT`). |
| `keywords` | Optional | Search tags for marketplace discovery. |

**Advanced:** optional path-override fields (`"commands": "./custom/path"`, `"mcpServers": "./x.json"`)
tell Claude Code to look outside the default folders. Rarely needed — the default convention suffices.

---

## Chunk 6 — The toy build (`/greet`)

We built a real minimal plugin, two files:

```
toy-greet-plugin/
├── .claude-plugin/plugin.json   ← identity metadata
└── commands/greet.md            ← the /greet command = a 2-gate workflow
```

`greet.md` *is* the workflow (Chunk 4 made concrete): frontmatter `description` + a body of ordered
prose — Phase 1 (collect) → **GATE 1** (confirm inputs) → Phase 2 (draft) → **GATE 2** (approve
final). Both are human-approval gates worded imperatively (Trap T3: "STOP … until APPROVED").
No Python, no loop code — the agent is the runtime obeying the prose.

**Scope tip:** a short workflow can live entirely inside the command file. Long/reusable workflows
belong in a **skill**, with the command as a thin caller. (We'll do the latter for the real product.)

---

## Q&A — Where plugins install & the dev flow (host pollution)

**Q: If we make a marketplace.json and run `/plugin install`, where does it go? Does it pollute my
global `~/.claude`?**

`/plugin install` does **two** things: (1) **registration** — a config entry (`enabledPlugins`) in a
settings file; (2) **materialization** — a cached copy of the plugin under `~/.claude/plugins`. So a
normal install **does write to your host `~/.claude`.**

Settings exist at **two scopes**: user-level (`~/.claude/settings.json`, global) and project-level
(`<project>/.claude/settings.json`, local to one folder). Installing project-scoped keeps the config
*entry* local — but the cached *copy* still lands in host `~/.claude/plugins`. Everything is
reversible (`/plugin uninstall`, `/plugin marketplace remove`).

**Takeaway:** to touch the host *not at all*, you need a separate environment — which is why we chose
a container (next). Exact `/plugin …` command syntax has shifted across versions — verify against
current docs before running (the `claude-code-guide` agent can confirm).

---

## Decision — Dev-container test sandbox

**Decision (2026-09-06):** test the plugin inside a **Docker dev container** with its own isolated
`~/.claude`, rather than installing into the host. Source stays in this repo (mounted into the
container); we run `/plugin marketplace add` + `install` *inside* the container.

**Why:** zero host footprint; disposable clean slate (`docker rm` to reset); it exercises the real
install path; and it's the correct **blast radius** for the final product, which *writes and commits
code*. So the sandbox is reused for `/implement-feature`, not just the toy.

**Settings:** interactive Claude login (no API key) · base adapted from Anthropic's official Claude
Code devcontainer · repo mounted in · container `~/.claude` on a named volume so login persists.

| Approach | Host pollution | Realism | Effort |
|---|---|---|---|
| **Dev container** (chosen) | **None** | **Full** | Medium (one-time) |
| Project-scoped host install | Cached copy only, reversible | Full | Low |
| Simulate run, no install | None | Low | Zero |

---

## Chunk 7 — Building the sandbox (devcontainer CLI + features)

A **dev container** = a Docker image with your tools + config saying "mount my code, drop me at a
shell." Because Claude Code's `~/.claude` lives *inside*, the host is never touched.

Our setup (Option A, modeled on `~/dev/hello-dev-container`):
- **`.devcontainer/` at the repo root** → the whole repo is the workspace (mounted at
  `/workspaces/<repo>`). Plugin source in `toy-greet-plugin/`; `test-toy-greet-plugin/` is the
  in-container scratch project.
- **Base:** `mcr.microsoft.com/devcontainers/python:3.12` + uv (the real product is Python).
- **Node.js + Claude Code via devcontainer *features*** — declared, so they survive rebuilds:
  ```jsonc
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},               // FIRST — provides npm
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  }
  ```
- **Login persistence:** `~/.claude` mounted to named volume `expt-skill-workflow-claude`;
  `postCreateCommand` chowns it to `vscode`; `DISABLE_AUTOUPDATER=1` pins the toolchain.

**Lifecycle** (see `DEVCONTAINER.md`): `devcontainer up --workspace-folder .` (build+start, idempotent),
`devcontainer exec … bash|claude`, teardown levels `stop → rm -f → volume rm → rmi`. VS Code: ⇧⌘P →
*Reopen in Container* / *Rebuild Container*.

---

## Q&A — `devcontainer up` vs plain `docker run`

**Q: Why use `devcontainer up` instead of a `docker run` script?**

- **`docker run`**'s only edge is needing no extra CLI. Otherwise it's a redundant third path.
- **`devcontainer up`** reads `devcontainer.json` and does build + create + mounts + **features** +
  **lifecycle hooks** (`postCreateCommand`) + `remoteUser` in one idempotent command — and the *same*
  config powers VS Code's "Reopen in Container." One source of truth, two front-ends.
- **Features > hand-installs:** `npm install -g …` in a Dockerfile is lost on rebuild and hit the
  documented "node present but npm missing" failure; the Node + Claude Code features solve both
  (declare Node *first* — T7).

**Takeaway:** for anyone already using the devcontainer CLI, `devcontainer up` + features is the
idiomatic, reproducible, VS-Code-compatible choice. We dropped `run.sh`.

---

## Chunk 8 — Install & run the toy (marketplace → install → gates)

We ran the toy end-to-end **inside the container** and watched the two gates fire — proving the
driverless-workflow pattern with real Claude Code.

The flow that worked:
1. `devcontainer up --workspace-folder .` — build + start (features installed Claude Code 2.1.260).
2. `devcontainer exec --workspace-folder . claude` — interactive login (persisted in the volume).
3. `/plugin marketplace add /workspaces/expt-skill-wotkflow-agent` — registered `toy-local-marketplace`.
4. `claude plugin install toy-greet@toy-local-marketplace` (CLI) → `/reload-plugins`.
5. `/toy-greet:greet` — Phase 1 collect → GATE 1 confirm → Phase 2 draft → GATE 2 approve. ✅

**Lessons learned (real ones from this run):**
- Typing `/plugin install X@Y` as a one-liner in the session can just **open the manager UI and
  no-op** (no confirmation printed). The **CLI** form `claude plugin install X@Y` is deterministic
  and scriptable; follow with `/reload-plugins` to activate in the current session. (Trap T8.)
- Verify with `claude plugin list` and `claude plugin marketplace list`.

---

## Q&A — `marketplace add` vs `install`

**Q: What does `/plugin marketplace add <path>` do?**

It **registers a catalog**, it does not install anything. Claude Code reads the
`.claude-plugin/marketplace.json` at that path, learns the marketplace `name` and its list of
plugins (each with `source`, `description`), and records it so those plugins become **installable by
name**. Like *subscribing to an app store's catalog* — not downloading an app. You then separately
`/plugin install <plugin>@<marketplace>` to materialize + activate one. Two steps on purpose: one
marketplace can list many plugins.

---

## Correction — plugin commands are namespaced (`/plugin:command`)

Earlier (Chunks 5–6) I said a file `commands/greet.md` becomes `/greet`. **For a plugin, commands are
namespaced by the plugin name:** `toy-greet-plugin/commands/greet.md` → **`/toy-greet:greet`**, never
bare `/greet`. (A file at `skills/greet/SKILL.md` would also surface as `/toy-greet:greet`.) The
namespacing prevents command-name collisions between installed plugins.

---

## Chunk 9 — Designing `/implement-feature`: conductor + isolated gates

The real product is a **conductor [C] + isolated-subagent [I]** system, not one agent walking one
context. The **conductor** is the interactive session: it holds the through-line, talks to the human,
and delegates the *bias-sensitive* gates to **isolated subagents** (fresh context, pinned model+
effort, a curated *file* inbox). The human is the **continuity thread** integrating independent
specialists. (Patterns P13–P20.)

**Why isolate?** "Bias" is two problems: **anchoring** (the reviewer who watched the code get written
shares the author's blind spots) → fixed by a **fresh context**; and **model monoculture** (one
model's blind spot at every gate) → fixed by **model/effort diversity at the critic gates**.

**The 11 gates** (see `PLAN.md` for the full table). Human gates bookend (0 classify, 1 interview,
2 spec, 9 review); machine-condition gates run the middle unattended (3–7). Standouts:

- **Gate 0 CLASSIFY** also proposes a **per-gate model/effort plan** the human approves — with the
  invariant **design & every review use a higher model than implementation** (P17).
- **Gate 1 INTERVIEW** captures functional ACs, **non-functional ACs** (scale/perf/security),
  explicit **constraints** (mandated/forbidden tech — P18), and a **boundary inventory**.
- **Gate 2 DESIGN** splits into `design-interface.md` (public contract) vs `design-internal.md`
  (algorithm, *withheld*), plus a **test plan** with coverage + mutation-kill thresholds.
- **Gate 3 WRITE-TESTS** is **algorithm-blind** (inbox = requirements + interface only) so tests
  encode the contract, not the code (P15).
- **Gate 4 TEST-REVIEW** — a *fresh* reviewer critiques the tests *before* implement (P16).
- **Gate 6 VERIFY** — drive the *real* function on the ACs; green tests alone are not Done (T10).
- **Gates 8–10** split what the original plan called "step 6": REVIEW-GUIDE → HUMAN REVIEW → COMMIT.

**Every handoff is a file** (P14) — a defined inbox/outbox per gate, never the raw transcript. Much
of this design was borrowed from the user's own validated `claude-sdlc` `/sdlc-feature-v2` prototype.

---

## Q&A — Borrow `grilling` vs delegate to it

**Q: Should Phase 1 delegate to the `grilling` skill, borrow its pattern, or skip it?**

**Borrow the pattern.** `grilling` models the interview as a **design tree** worked in **rounds**:
each round asks the whole *frontier* (every question whose prerequisites are settled), one numbered
question at a time **with a recommended answer**, then waits. Facts are the agent's job (dispatch a
sub-agent to look them up); decisions are the user's. Done when the frontier is empty.

We **bake that mechanic into our Gate 1 prose** rather than hard-delegating, because delegating (a)
adds a plugin dependency the sandbox must carry, and (b) `grilling` stops at "shared understanding" —
it doesn't emit our structured `requirements.md` (ACs + constraints + boundary inventory). Borrowing
keeps us dependency-free and in control of the output artifact. (Pattern P19.)

---

## Q&A — Why per-gate models need agent-definition files

**Q: To run each gate on a different model/effort, why not just set the model on the Task call?**

The Task/Agent tool can set a subagent's **model** inline, but **not its reasoning effort**. To pin
*both* (and to keep briefs reusable + versionable), each isolated gate becomes a **named agent type**
defined in a file — `.claude/agents/<role>.md` — whose frontmatter carries `model`, effort, and
`tools`, and whose body is the reusable brief. The conductor then spawns that agent by name. This is
also how we enforce the *review > implementation* model invariant deterministically. (Pattern P17.)

---

## Q&A — Proving isolation & tracking usage (observability)

**Q: How can the workflow *prove* different subagents ran, that each read only its inbox, and track
model/token usage?**

An **analysis capability** with two data sources (P20):
- **Live `run-log.jsonl`** — the conductor appends an entry as each gate completes (declared agent,
  model, inbox). This is orchestration *state*, but self-reported.
- **Session transcript JSONL** (`~/.claude/projects/<slug>/*.jsonl`) — Claude Code records per-message
  model + token usage + tool calls, including subagent sidechains. This is the **ground truth**; the
  conductor can't read a subagent's internal token count from the Task return value (T13), so real
  proof means parsing the transcript.

Isolation is enforced **preventively** (restrict each agent's tools/paths, or `isolation: worktree`,
so it *can't* read outside its inbox) **and** verified **detectively** (audit the files it actually
read vs its declared inbox). The analyzer is a **deterministic Python parser** → per-gate
model/tokens/tools/files-read + isolation-compliance verdict + cost table. It's *measurement* code,
not orchestration, so it doesn't break the driverless principle. (Feasibility: confirm the transcript
schema in the sandbox before relying on it.)

---

## Chunk 10 — Scaffolding the conductor + agent-definition files

We built the real product's skeleton, `implement-feature-plugin/`:
```
implement-feature-plugin/
├── .claude-plugin/plugin.json
├── toolchain/requirements-dev.txt            # pinned dev tools
├── commands/implement-feature.md             # THIN → loads the skill
├── skills/implement-feature/
│   ├── SKILL.md                              # conductor score (Gate 0 full; 1–10 stubbed)
│   └── references/quality-standards.md        # Definition of Done (single source of truth)
└── agents/{test-writer,test-reviewer,implementer,verifier,code-reviewer}.md
```

**Two structural moves:**
- **Thin command, heavy skill (P21).** A command file is *always* resident in context; a skill body
  loads *on demand*. So `implement-feature.md` just loads the `implement-feature` skill, whose
  `SKILL.md` holds the 11-gate score. Keeps context lean when the command isn't in use.
- **Each isolated gate = an agent-definition file.** `agents/*.md` frontmatter pins **model +
  effort + tools** (mirroring the `claude-sdlc` shape): `model:`, `effort: high`, `tools:`,
  `disallowedTools:`. Reviewers/verifier are **read-only** (`disallowedTools: Write, Edit`) — which
  buys *independence*, not just safety (T14): a critic that could edit might silently hide a problem.
  The test-writer's body forbids reading `design-internal.md` (the algorithm-blind rule, P15).

Gate 0 is written in full: a **hard-fail preflight**, the **workdir**, and the **editable model plan**.
Gates 1–10 are one-line stubs we flesh in later chunks.

---

## Q&A — Where do lint/type/concurrency checks live, and how are tools guaranteed?

**Q: The scaffold named pytest + mutation but no linting, type-safety, or concurrency checks — where
do those run, with what tools, and how do we ensure they're installed?**

**Split the checks by speed (P23):**

| Check | Tool | Runs at |
|---|---|---|
| Lint + format | `ruff` | IMPLEMENT inner loop (part of "green") |
| Type safety | `mypy` | IMPLEMENT inner loop (part of "green") |
| Unit tests | `pytest` | IMPLEMENT inner loop |
| Coverage | `pytest-cov` | CODE-REVIEW (vs test-plan threshold) |
| Mutation kill | `mutmut` | CODE-REVIEW (vs test-plan threshold) |
| Concurrency | `hypothesis`/`pytest-asyncio`/stress | situational — boundary-driven (P25) |

So the implementer's **inner-loop "green" = pytest + ruff + mypy all clean**; coverage + mutation are
the reviewer's slow checks. **Type checker = `mypy`** (the conventional production *CI-gate* choice;
pyright stays an editor complement).

**Guaranteeing the tools (P22):** because the workflow is prescriptive about the **dev container**, we
(1) pin them in `toolchain/requirements-dev.txt`, (2) install them in the container via
`postCreateCommand` (`uv pip install --system -r …`), and (3) run a **Gate 0 preflight** that
hard-fails if any tool is missing — nothing proceeds on a broken environment. The *tool commands* live
once in `quality-standards.md`; the *threshold numbers* are per-feature and live in Gate 2's test plan
(P24). **Concurrency** has no single Python tool, so it's mandated by the test plan only when the
boundary inventory shows the feature is concurrent/async — otherwise skipped with a stated reason.

---

## Chunk 11 — Gate 1: the grilling-style INTERVIEW

Gate 1 turns a one-line request into `requirements.md`. **Method (borrowed from `grilling`, P19):**
model the feature as a **design tree**; work it in **rounds**; each round ask the whole **frontier**
(questions whose prerequisites are settled), one numbered question at a time **with a recommended
answer**, then wait. **Facts are the agent's job** — dispatch a subagent to look up anything in the
environment (keeps the conductor's context lean; only the fact returns). **Decisions are the human's.**
Done when the frontier is empty — nothing silently assumed.

**Four mandatory buckets** (schema in `references/requirements-template.md`): functional ACs ·
non-functional ACs (scale/perf/security) · constraints (mandated/forbidden tech — P18) · boundary
inventory (each boundary + how it's exercised un-mocked; "None (pure feature)" is a *required*
explicit answer — T17). Then **summarize → STOP-until-APPROVED → write the file** (T16: the artifact's
existence equals its blessing).

---

## Q&A — Our Gate 1 vs the `grilling` skill

**Q: How does our Gate 1 compare to the installed mattpocock `grilling` skill?**

**Same engine, different wrapper.** We copied grilling's *interview algorithm* verbatim in spirit
(design tree · rounds · frontier · numbered Qs with recommended answers · facts-via-subagent · done
when frontier empty · same `❓ … ➡️` format). We then wrapped it for pipeline use (P26):

| | `grilling` skill | Our Gate 1 |
|---|---|---|
| Purpose | Sharpen *any* plan/idea | Produce `requirements.md` |
| Completion | Frontier empty → "shared understanding" | Frontier empty **AND** four buckets covered |
| Output | *Explicitly none* ("do not act") | Durable artifact via template, consumed downstream |
| Approval | Soft ("don't act until confirmed") | Formal STOP-until-APPROVED + outbox + run-log |
| Context | Standalone, ephemeral | One gate in the conductor score |

Trade-off of *borrowing* (vs delegating to `grill-me`): no plugin dependency and we control the
artifact, but we don't auto-inherit upstream improvements to `grilling`. (`grill-me` itself is just a
one-line manual launcher for `grilling` with `disable-model-invocation: true`.)

---

## Chunk 12 — Gate 2: DESIGN/SPEC + the interface/internal split + test plan

Gate 2 reads `requirements.md` and writes **three** handoff files:
- **`design-interface.md`** — the *public contract only* (signatures, types, I/O, observable
  error/edge behavior, invariants). **Shared** with the test-writer.
- **`design-internal.md`** — the *algorithm*, data structures, alternatives, complexity, quality
  expectations, risks. **Withheld** from the test-writer; seen by implementer + reviewers.
- **`test-plan.md`** — enumerated tests (unit/api/e2e) each traced to an AC or boundary, plus the
  coverage + mutation-kill **thresholds** and a concurrency plan (mandated iff the feature is
  concurrent/async).

**Why the split is the mechanism (P15):** if the algorithm leaked into the interface, the test-writer
would derive tests *from the algorithm* → tests encode the implementation's own assumptions → a wrong
implementation sharing those assumptions still passes. Splitting forces tests to encode the
**contract**, so they can *fail* a bad implementation. Close: present approach + alternatives + files →
**STOP-until-APPROVED** → write.

---

## Q&A — Why thresholds live in the test plan, and why record alternatives

**Q1: Why put the coverage/mutation numbers in the per-feature `test-plan.md` instead of in the shared
`code-reviewer.md` agent?** Because the thresholds are **risk-dependent per feature** (payments → 95%;
log formatter → 80%). `code-reviewer.md` is a *shared, versioned* agent reused across every run;
hardcoding a number there forces one global value and an edit to the shared agent per feature. The test
plan lets the human set them at Gate 2, and the reviewer reads them generically. That's **P24**:
universal *commands* in `quality-standards.md`, per-feature *numbers* in the test plan.

**Q2: Why record rejected alternatives, not just the chosen design?** It's an **ADR** (architecture
decision record — P27). Two months later, "why this and not that?" is answerable from the file instead
of lost; and the code-reviewer can check the chosen approach still holds against what was rejected.

---

## Chunk 13 — Gate 3: WRITE-TESTS + validating & enforcing subagent isolation

**Gate 3** is where the conductor first **delegates**: it spawns the algorithm-blind `test-writer` as an
isolated subagent (`subagent_type: implement-feature:test-writer` — plugin agents are **namespaced**).
The agent-def file pins its *static identity* (model/effort/tools); the spawn **brief** passes the
*per-run* specifics (workdir, the ONLY-inbox = requirements + design-interface + test-plan, the "do not
read design-internal" rule). Exit is a machine condition: the suite must be **red for the right reason**
(implementation absent), not from import errors.

**The deviation that mattered.** Before building five more gates on the assumption that we can *actually*
pin a subagent's model/effort/tools and confine its reads, we validated it. The result (full report:
`LAUNCHING-SUBAGENTS.md`; investigation: `design/isolation-experiments.md`):

- **Model** pinning works and is transcript-verifiable; **tools** allow/deny is a hard block; **effort**
  pins via agent-def frontmatter only (no inline override).
- **Reads** can be both **audited** and **confined**. The winning mechanism is a **plugin PreToolUse
  guard hook** that fires for the conductor *and* every subagent (a *project*-settings hook did **not**
  fire headless) and keys on the stdin **`agent_type`**.
- **Bug caught by testing, not docs:** plugin agents are namespaced (`plugin:agent`), not bare.

---

## Q&A — How is subagent isolation actually enforced (the guard hook)?

**Q: We give the test-writer a brief saying "don't read design-internal.md" — but it has a Read tool.
What actually stops it, and how do we prove what any agent read?**

A single **plugin-shipped PreToolUse hook** (`implement-feature-plugin/hooks/hooks.json` →
`hooks/scripts/guard.py`), matching `Read|Bash|Grep|Glob`, does three jobs on every call — from the
conductor *and* every subagent:
1. **Audit** — appends `{ts, agent_type, agent_id, tool, target}` to a run-log (a stable, attributable
   record of every read — better than parsing the version-unstable transcript).
2. **Secrets guardrail** — denies reading `.env`, keys, credentials, `~/.ssh/` — for **all** agents.
3. **Per-agent blindness** — denies `design-internal.md` for the **test-writer** only (matched on
   `agent_type`), Read *and* Bash; other critics may read it.

A hook `deny` decision + exit code 2 **hard-blocks** the call. This is **defense-in-depth** with the
agent's own role instruction (P29): in testing, the test-writer refused on its own before the hook even
fired. Model/token figures still come from the transcript (best-effort). Key lesson (T21): the docs were
wrong on agent naming and unsure on headless hooks — we **verified empirically** before depending on it.
