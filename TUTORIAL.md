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
