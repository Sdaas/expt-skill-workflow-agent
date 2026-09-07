# expt-skill-workflow-agent

A **hands-on tutorial project** for learning how to build a Claude Code **plugin** that drives a
full human-in-the-loop workflow using **skills + subagents + workflow patterns** (no orchestration
code). We build up to an `/implement-feature` command: interview → interface/behavioral spec (with
approval) → test-first implementation → deep review + mutation testing → final review → commit.

This is a **learning exercise, not production code.**

## How the tutorial runs
Chunked (~200–250 words each) + build steps. One chunk at a time; advance only on "next."
To continue in a new session: open `RESUME.md` and say **"read RESUME.md and continue."**

## Repo map
| Path | What it is |
|---|---|
| `PLAN.md` | The full 18-chunk tutorial plan + change-of-direction log. |
| `RESUME.md` | Live progress tracker + resume pointer. **Start here in a new session.** |
| `TUTORIAL.md` | Accumulating reference of concepts + captured Q&A. |
| `PATTERNS.md` | Running checklist: design patterns, anti-patterns, traps. |
| `DEVCONTAINER.md` | Dev container lifecycle (CLI) + VS Code ⇧⌘P command reference. |
| `.devcontainer/` | The dev container definition (Option A: repo root = workspace). |
| `toy-greet-plugin/` | The **toy plugin** — a `/greet` 2-gate workflow (Part B, learning scaffold). |
| `test-toy-greet-plugin/` | In-container **scratch project** where we install + run `/greet`. |

## Testing model
We never install the plugin into the Mac's global `~/.claude`. Instead we run Claude Code inside a
**dev container** with its own isolated `~/.claude`, managed via the `devcontainer` CLI / VS Code.
See `DEVCONTAINER.md`. This same sandbox is reused for the real product (which commits code).

## Status
Foundations (Part A) complete; toy plugin scaffolded; dev-container sandbox built. Next: install and
run the toy inside the container (Chunk 8). See `RESUME.md` for the exact current position.

---
Authorship: Soumendra Daas &lt;soumendra.daas@gmail.com&gt;
