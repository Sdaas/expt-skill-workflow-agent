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
A plugin exposing an `/implement-feature` slash command that runs a human-in-the-loop workflow:
1. Interview the user for functional requirements, error conditions, edge cases (loop until clear).
2. Produce an **interface + behavioral spec** (no implementation) and get user approval.
3. TDD: write failing tests from the spec.
4. Implement → quick code review → run tests; loop until green.
5. Deep review (Python best practices, error handling) + mutation testing; fix impl/tests; loop.
6. Present a summary for human review, then commit on approval.

Driven by **skills + subagents + workflow patterns** — no hand-written orchestration code.

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
9. Decompose `/implement-feature` into phases + gates; decide inline vs subagent per phase.

### Part D — Build the real product
10. Scaffold the plugin + `/implement-feature` command shell.
11. Phase 1 — requirements interview (loop-until-clear).
12. Phase 2 — interface + behavioral spec, human approval gate.
13. Phase 3 — TDD: write failing tests from the spec.
14. Phase 4 — implement → quick review → run tests, loop to green.
15. Phase 5 — deep review + mutation-testing loop.
16. Phase 6 — final human review gate → commit.
17. End-to-end dry run on a sample Python feature — inside the sandbox container.

### Part E — Wrap
18. Package, install, recap concepts → where each showed up in the build.

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

## Change-of-direction log
- 2026-09-06 — **Testing strategy decided: dev-container sandbox.** Instead of installing the
  plugin into the host's global `~/.claude`, we test inside a Docker dev container that has its own
  isolated `~/.claude`. Rationale: zero host footprint; disposable clean slate; correct blast radius
  for a workflow that eventually *commits code*. Reused for both the toy and the final product.
  Decisions: **interactive Claude login** (no API key); **base = adapted from Anthropic's official
  Claude Code devcontainer**; repo mounted into the container; container `~/.claude` persisted via a
  named volume so login survives restarts. Sandbox lives in `test-toy-greet-plugin/`.
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
