# Tutorial Plan: Building `/implement-feature` as a Claude Code Plugin

**Approved:** 2026-09-06

## Learning contract
- Each numbered chunk = ~200–250 words of teaching + a comprehension check.
- Advance only when the user says "next" (or similar).
- Combination of tutorial + hands-on build. Not production — a learning exercise.
- Target language for the generated feature code: **Python**.
- Decisions locked: **toy first → then real product**; **build from scratch** (no dissecting
  existing installed skills); **solid foundations before writing any files**.

## The product we are ultimately building
A plugin exposing an `/implement-feature` slash command that runs a human-in-the-loop workflow as a
**conductor [C] + isolated-subagent [I]** system (design finalized in Chunk 9, 2026-09-07). The
conductor is interactive/human-facing and holds the through-line; bias-sensitive gates run as
**isolated subagents** (fresh context, pinned model+effort, curated file inbox). Every handoff is a
**file**, never the raw transcript. The 11-gate sequence:

| # | Gate | Approver | Where·model | Inbox | Outbox |
|---|------|----------|-------------|-------|--------|
| 0 | CLASSIFY + **model plan** | 👤 confirm | [C] Opus | request | proposed model/effort table (user adjusts) |
| 1 | INTERVIEW *(grilling rounds)* | 👤 APPROVED | [C] Opus | — | `requirements.md` — functional **+ non-functional ACs** (scale/perf/security) + **constraints** (mandated/forbidden tech) + **boundary inventory** |
| 2 | DESIGN/SPEC + **test plan** | 👤 APPROVED | [C] Opus | requirements | `design-interface.md`, `design-internal.md`, test list (unit/api/e2e) + coverage & mutation-kill thresholds |
| 3 | WRITE-TESTS *(blind)* | ⚙️ red | [I] Sonnet | requirements + **design-interface only** | `tests/` + `test-intent.md` |
| 4 | TEST-REVIEW | ⚙️ APPROVE (bounded loop) | [I] Opus | requirements + full design + tests | `test-review-findings.md` |
| 5 | IMPLEMENT | ⚙️ unit green (inner loop) | [I] Sonnet | tests + full design | `src/` |
| 6 | VERIFY | ⚙️ ACs/e2e pass (outer loop) | [I] Sonnet | ACs + boundary inventory | verify report |
| 7 | CODE-REVIEW + mutation | ⚙️ APPROVE + kill-rate ≥ thr (bounded) | [I] Opus | requirements + design + whole diff | `code-review-findings.md` |
| 8 | REVIEW-GUIDE | — | [C] Sonnet | changed files | change map + finding pointers |
| 9 | HUMAN REVIEW | 👤 APPROVED | [C] | everything | — |
| 10 | COMMIT | 👤 post-approval | [C] Sonnet/Haiku | — | commit |

Plus a cross-cutting **observability / analysis capability** (see below). Driven by **skills +
subagents + workflow patterns** — no hand-written *orchestration* code (the analyzer is deterministic
*measurement* code, which is allowed).

## Observability / analysis capability (added 2026-09-07)
The workflow must be able to **prove and measure** what it did, to understand and optimize it:
- **Prove** distinct subagents ran, and each read **only** its designated inbox.
- **Track** per-gate model + token usage + tool calls + loop iterations.
- **Capture** what happened inside each subagent (brief, actions, output).

Design (all four decisions = recommended option, 2026-09-07):
- **Data source = both.** Conductor writes a live `run-log.jsonl` as each gate completes (declared
  agent/model/inbox = orchestration state); a post-hoc analyzer parses the Claude Code **session
  transcript JSONL** (`~/.claude/projects/<slug>/*.jsonl`) for ground-truth model/tokens/tool-calls/
  files-read = the actual proof.
- **Isolation = preventive + detective.** Restrict each agent's tools/paths (or `isolation: worktree`)
  so it *can't* read outside its inbox, **and** audit the transcript afterward to prove it didn't.
- **Analyzer = deterministic Python parser** (dogfoods our Python target): transcript JSONL →
  per-gate model/tokens/tools/files-read + isolation-compliance verdict + cost table.
- **Feasibility caveat:** confirm the transcript JSONL schema (per-message usage + subagent sidechains)
  inside the sandbox before relying on it.

**UPDATE (2026-09-07 — validated, Chunk 13 deviation).** The mechanisms were empirically validated and
the primary one changed. See `design/isolation-experiments.md` and the root report
`LAUNCHING-SUBAGENTS.md`. Outcomes: model pinning, tool hard-block, and read-audit are **proven**;
effort pins via agent-def frontmatter only (no inline override). The **audit + secrets guardrail +
per-agent blindness** are now enforced by a **plugin PreToolUse guard hook**
(`implement-feature-plugin/hooks/`) that fires for the conductor *and* every subagent in headless (a
*project*-settings hook did not) and keys on `agent_type`: it logs every Read/Bash, denies
secrets/`.env`/keys for ALL agents, and denies `design-internal.md` for the test-writer only. The
transcript-parse analyzer is retained as a **best-effort** source for per-agent model/tokens (format is
officially unstable); the hook run-log is the stable audit. Analyzer still to be promoted into the
plugin at the observability chunk.

## Chunks

### Part A — Foundations (concepts, no files)
1. Four building blocks: skill vs slash command vs subagent vs plugin — how they nest.
2. Anatomy of a skill: `SKILL.md`, frontmatter, progressive disclosure.
3. Subagents: isolated context, delegation, what they return.
4. The "workflow" pattern: one skill scripting multi-gate human-in-the-loop processes — why no driver code is needed.
5. Plugin packaging: directory layout, manifest, how install exposes the command.

### Part B — Test sandbox + toy run
6. Scaffold a minimal plugin with one command: a 2-gate "greet" workflow (ask → confirm → act). ✅ DONE
7. **Build the disposable test sandbox** — a dev container managed via the `devcontainer` CLI
   (Option A: `.devcontainer/` at the **repo root**, whole repo = workspace). Node.js + Claude Code
   via devcontainer **features**; interactive login inside the container; login persisted in the
   named volume `expt-skill-workflow-claude`. Host `~/.claude` is never touched. `test-toy-greet-plugin/`
   is the in-container scratch project. Reused to test the real product later. Teaches: dev containers,
   the `devcontainer` CLI + VS Code ⇧⌘P workflow, and runtime isolation. (See `DEVCONTAINER.md`.)
8. ✅ DONE — Inside the container: `marketplace.json` verified; `/plugin marketplace add` +
   `claude plugin install`; ran `/toy-greet:greet` end-to-end, both gates fired. (Live-edit demo deferred.)

### Part C — Design the real product
9. ✅ DONE (2026-09-07) — Decomposed `/implement-feature` into the 11-gate conductor + isolated-gate
   design above; decided inline [C] vs subagent [I] per gate; chose per-gate model tiers (review >
   implementation invariant); borrowed the `grilling` round-based interview pattern; folded in the
   interface/internal design split + TEST-REVIEW gate + VERIFY-observed from the validated
   `claude-sdlc` `feature-as-workflow` WIP; added the observability/analysis capability. Design chunk
   (no product files yet). Research sources: `grilling` skill, `/sdlc-feature` v1, and the user's
   `claude-sdlc` `/sdlc-feature-v2` prototype + `design/gate-isolation-prototype.md`.

### Part D — Build the real product (re-planned 2026-09-07 for the 11-gate design)
10. Scaffold the plugin + `/implement-feature` **conductor** shell + Gate 0 CLASSIFY/model-plan +
    the `.claude/agents/*.md` **agent-definition files** (pin model+effort per isolated gate).
11. Gate 1 — INTERVIEW: grilling-borrowed rounds → `requirements.md` (functional + non-functional
    ACs + constraints + boundary inventory). Human-approval gate.
12. Gate 2 — DESIGN/SPEC: interface/internal split + test plan (coverage + mutation thresholds).
    Human-approval gate.
13. Gate 3 — WRITE-TESTS: isolated, algorithm-blind test-writer (inbox = requirements +
    design-interface only); confirm red.
14. Gate 4 — TEST-REVIEW: isolated fresh reviewer; bounded loop back to write-tests.
15. Gate 5 — IMPLEMENT: isolated implementer, inner loop to unit-green.
16. Gate 6 — VERIFY: isolated; outer loop; drive the real function on ACs + boundaries un-mocked.
17. Gate 7 — CODE-REVIEW + mutation: isolated whole-diff reviewer; kill-rate gate; bounded loop.
18. Gates 8–10 — REVIEW-GUIDE → HUMAN REVIEW → COMMIT.
19. **Observability/analysis** — the **guard hook** (audit log + secrets guardrail + per-agent read
    denial) is already built + validated in Chunk 13; this chunk promotes the deterministic Python
    analyzer into the plugin (combine hook run-log for reads + transcript for model/token/cost).
20. End-to-end dry run on a sample Python feature — inside the sandbox container.

### Part E — Wrap
21. Package, install, recap concepts → where each showed up in the build.

## File conventions
- Deliverables live under this folder (`expt-skill-wotkflow-agent/`).
- Temp/scratch files go to `/tmp/` or end in `.tmp`, and are deleted when done.

## Standing instructions added during the session (keep for all future sessions)
1. Pacing: one chunk → comprehension check → advance only on the user's "next."
2. Update `RESUME.md` / `TUTORIAL.md` / `PATTERNS.md` **only** when the user advances ("next").
3. Whenever the user asks a mid-chunk question, capture a condensed Q&A into `TUTORIAL.md` at
   the next advance.
4. Maintain `PATTERNS.md` — a running design-patterns / anti-patterns / traps checklist to apply
   when building the toy and the real solution.
5. Commit each chunk before moving on: on every "next", after recording docs, commit all of that
   chunk's changes (one commit per chunk). Never accumulate multiple chunks of uncommitted work.
   (Added 2026-09-07.)

## Change-of-direction log
- 2026-09-09 — **Gate 7 CODE-REVIEW: typed-finding routing + six-dimension rubric.** Fixed a routing
  bug — coverage/mutation failures looped back to IMPLEMENT, but the implementer cannot edit tests
  (guard job #4), a dead end. Now each review finding is tagged `→IMPLEMENT` (code defect) or
  `→TESTS` (weak/missing test → re-enter WRITE-TESTS + TEST-REVIEW); the conductor routes each.
  Kept **one review pass / one gate, two repair paths** (not a second phase — the pass is shared;
  only the correction target differs). Also replaced the ad-hoc checklist with the six `claude-sdlc`
  quality dimensions (best practices, performance, testing pyramid, security, reliability,
  observability). See P37/P38. (Surfaced during a Chunks 14–18 walk-through.)
- 2026-09-06 — **Testing strategy decided: dev-container sandbox.** Instead of installing the
  plugin into the host's global `~/.claude`, we test inside a Docker dev container that has its own
  isolated `~/.claude`. Rationale: zero host footprint; disposable clean slate; correct blast radius
  for a workflow that eventually *commits code*. Reused for both the toy and the final product.
  Decisions: **interactive Claude login** (no API key); **base = adapted from Anthropic's official
  Claude Code devcontainer**; repo mounted into the container; container `~/.claude` persisted via a
  named volume so login survives restarts. Sandbox lives in `test-toy-greet-plugin/`.
- 2026-09-07 — **Chunk 9: `/implement-feature` re-designed as conductor + isolated gates.** Grew from
  the original 6 steps to an 11-gate sequence after researching three sources: the `grilling` skill
  (borrowed its design-tree/round/recommended-answer interview pattern for Gate 1), the shipped
  `/sdlc-feature` v1, and — decisively — the user's own `claude-sdlc` `/sdlc-feature-v2` prototype on
  branch `feature-as-workflow` (`design/gate-isolation-prototype.md`, already A/B-validated). Folded in
  from v2: curated inbox/outbox handoff contract, interface/internal design split (algorithm-blind
  test-writer), a new TEST-REVIEW gate before implement, model/effort plan proposed at CLASSIFY with
  the review>implementation invariant, effort pinned via agent-definition files, VERIFY-observed.
  User additions: (1) INTERVIEW explicitly captures technology/design **constraints** ("use jdbc not
  spring"); (2) an **observability/analysis capability** (prove distinct agents ran + read only their
  inbox; track model/token/tool usage; deterministic Python transcript analyzer). Decisions locked via
  four + three AskUserQuestion picks (all recommended). Relationship to `claude-sdlc`: this stays a
  **from-scratch teaching build** that borrows v2's proven decisions; the two repos stay separate.
- 2026-09-07 — **Refined to Option A + `devcontainer` CLI.** Adopted the user's `~/dev/hello-dev-container`
  conventions: `.devcontainer/` moved to the **repo root** (whole repo = workspace); dropped the plain
  `docker run` path (`run.sh` removed); Node.js + Claude Code installed via devcontainer **features**
  (not hand `npm install`); base `mcr.microsoft.com/devcontainers/python:3.12` + uv; login volume
  `expt-skill-workflow-claude`; `postCreateCommand` chown; `DISABLE_AUTOUPDATER=1`. Managed via
  `devcontainer up/exec` + VS Code ⇧⌘P. Added `DEVCONTAINER.md` (lifecycle + palette) and a repo-root
  `README.md`. `test-toy-greet-plugin/` is now the in-container scratch project.

## Companion docs
- `RESUME.md` — live progress + resume pointer.
- `TUTORIAL.md` — accumulating concept reference + captured Q&A.
- `PATTERNS.md` — design-patterns/anti-patterns/traps checklist.
