# RESUME — Tutorial Progress Tracker

> To continue in a new session: open this file and say **"read RESUME.md and continue."**

## How this tutorial works
Chunked tutorial (~200–250 words each) + hands-on build. Teach a chunk → comprehension
check → advance only when the user says "next." See `PLAN.md` for the full 17-chunk plan,
`TUTORIAL.md` for the accumulating concept reference, and `PATTERNS.md` for the running
design-patterns/anti-patterns/traps checklist we apply when building.

## Standing instructions (apply every session)
1. **Pacing:** teach one chunk → comprehension check → advance only on the user's "next."
2. **Doc-update timing:** update `RESUME.md` / `TUTORIAL.md` / `PATTERNS.md` **only** when the
   user says "next" (advances), never mid-chunk.
3. **Capture questions:** whenever the user asks a question mid-chunk, add a condensed Q&A of it
   (and the answer) into `TUTORIAL.md` at the next advance.
4. **Patterns checklist:** keep capturing design patterns / anti-patterns / traps in `PATTERNS.md`
   as they arise — the checklist we'll apply when building the toy and the real solution.
5. **Files:** deliverables under this folder; temp files in `/tmp/` or `*.tmp`, deleted when done.

## Status
- **Current phase:** Part A — Foundations
- **Last completed chunk:** Chunk 7 — Dev-container sandbox built (Option A, `devcontainer` CLI).
  Added `DEVCONTAINER.md`, repo-root `README.md`, `.gitignore`. Git repo initialized + first commit.
- **Next chunk to deliver:** Chunk 8 — Verify exact `/plugin` commands (offer `claude-code-guide`
  agent), add `marketplace.json`, `devcontainer up`, install the toy, run `/greet` through its gates.
- **Awaiting from user:** "next" to start Chunk 8.

## Progress log
- 2026-09-06 — Plan approved. Created `PLAN.md`, `RESUME.md`, `TUTORIAL.md`.
- 2026-09-06 — Delivered Chunk 1 (four building blocks).
- 2026-09-06 — Delivered Chunk 2 (anatomy of a skill).
- 2026-09-06 — Delivered Chunk 3 (subagents). Added `PATTERNS.md` running checklist per user request.
- 2026-09-06 — Delivered Chunk 4 (workflow pattern & gates). Added P6–P9, T3 to PATTERNS.md.
- 2026-09-06 — Delivered Chunk 5 (plugin packaging) + manifest Q&A. Recorded standing instructions.
- 2026-09-06 — Chunk 6 (toy build): created `toy-greet-plugin/` (plugin.json + commands/greet.md).
- 2026-09-06 — Fixed authorship to Soumendra Daas / soumendra.daas@gmail.com (memory + files).
- 2026-09-06 — Decided testing strategy: dev-container sandbox (see Key decisions). Captured dev-flow
  Q&As into TUTORIAL.md; added P10/T4 to PATTERNS.md. Revised PLAN (Part B, 18 chunks).
- 2026-09-07 — Chunk 7: built dev-container sandbox (Option A, devcontainer CLI, features), mirroring
  `~/dev/hello-dev-container`. Added `.devcontainer/`, `DEVCONTAINER.md`, repo-root `README.md`,
  `.gitignore`. Captured devcontainer Q&A + P11 in TUTORIAL/PATTERNS. `git init` + first commit.

## Key decisions
- Toy first → then real product.
- Build from scratch; do not dissect existing installed skills.
- Solid foundations before writing files.
- Target code language: Python.
- **Testing strategy = dev-container sandbox** (decided 2026-09-06; refined 2026-09-07 to Option A).
  Test the plugin inside a Docker dev container with its own isolated `~/.claude`; never install
  into the host global `~/.claude`.
  - Interactive Claude login (no API key).
  - **Managed via the `devcontainer` CLI** (`devcontainer up/exec`) + VS Code, modeled on the user's
    `~/dev/hello-dev-container` conventions — NOT plain `docker run` (the old `run.sh` was removed).
  - **Option A layout:** `.devcontainer/` at the **repo root** (whole repo = workspace, mounted at
    `/workspaces/expt-skill-wotkflow-agent`). `test-toy-greet-plugin/` is the in-container **scratch
    project** where we install + run `/greet`. Plugin source stays in `toy-greet-plugin/`.
  - Base: `mcr.microsoft.com/devcontainers/python:3.12` + uv; Node.js + Claude Code via devcontainer
    **features** (node feature first, then `anthropics/devcontainer-features/claude-code`).
  - Container `~/.claude` persisted via named volume `expt-skill-workflow-claude`; `postCreateCommand`
    chowns it to `vscode`. `DISABLE_AUTOUPDATER=1`.
  - Reused to test the final product (which commits code).
  - Authorship identity everywhere: **Soumendra Daas / soumendra.daas@gmail.com** (never Skye).

## Artifacts built so far
- `toy-greet-plugin/.claude-plugin/plugin.json` — toy plugin manifest
- `toy-greet-plugin/commands/greet.md` — `/greet` command implementing a 2-gate workflow
- `.devcontainer/Dockerfile` — mcr python:3.12 base + uv (Option A, repo root)
- `.devcontainer/devcontainer.json` — features (node + claude-code), volume, postCreate chown
- `DEVCONTAINER.md` — devcontainer lifecycle (CLI) + VS Code ⇧⌘P command reference
- `test-toy-greet-plugin/README.md` — the in-container scratch project (install + run `/greet`)
