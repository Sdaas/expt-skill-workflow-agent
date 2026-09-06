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
- **Last completed chunk:** Chunk 6 — Toy plugin scaffolded (`toy-greet-plugin/`). Plus captured
  dev-flow Q&As and decided the testing strategy (dev-container sandbox).
- **Next chunk to deliver:** Chunk 7 — Build the disposable dev-container test sandbox in
  `test-toy-greet-plugin/` (adapt Anthropic's official Claude Code devcontainer).
- **Awaiting from user:** "next" to build the sandbox.

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

## Key decisions
- Toy first → then real product.
- Build from scratch; do not dissect existing installed skills.
- Solid foundations before writing files.
- Target code language: Python.
- **Testing strategy = dev-container sandbox** (decided 2026-09-06). Test the plugin inside a Docker
  dev container with its own isolated `~/.claude`; never install into the host global `~/.claude`.
  - Interactive Claude login (no API key).
  - Base adapted from Anthropic's official Claude Code devcontainer.
  - This repo is mounted into the container (plugin source stays here).
  - Container `~/.claude` persisted via a named volume so login survives restarts.
  - Sandbox folder: `test-toy-greet-plugin/`. Reused to test the final product (which commits code).
  - Authorship identity everywhere: **Soumendra Daas / soumendra.daas@gmail.com** (never Skye).

## Artifacts built so far
- `toy-greet-plugin/.claude-plugin/plugin.json` — toy plugin manifest
- `toy-greet-plugin/commands/greet.md` — `/greet` command implementing a 2-gate workflow
