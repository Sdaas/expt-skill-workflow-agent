# Launching & Isolating Sub-Agents — Guidelines

A sub-agent is a fresh Claude instance you spawn (via the Task/Agent tool) to do one
focused job in its own context window. That power comes with a control problem: a
sub-agent starts with broad default capabilities, so **launching one safely means
deciding, up front, what it runs as, what it can touch, and how you will know what it
did.** This report states those problems and the supported mechanism for each.

It is written to be reusable across projects. Where a concrete example helps, it refers to
the `implement-feature` plugin in this repo (a conductor that spawns isolated, model-pinned
gate agents), but the guidance is general.

---

## Part 1 — The problems (what you must control)

**P1. Which model does it run on?**
Different jobs deserve different models. A reviewer or designer should use a stronger model
than an implementer; a mechanical step can use a cheap, fast one. Without explicit control,
a sub-agent silently inherits the parent's model, so cost and quality are left to chance and
the "reviewer must be stronger than the author" invariant cannot be guaranteed.

**P2. How hard does it think (reasoning effort)?**
Model alone is not the whole story — effort level materially changes depth and cost. You
need to pin effort per role, independently of the model, and know whether it can be set at
spawn time or must be declared in advance.

**P3. Which tools can it use — and which must it NOT?**
A reviewer should be able to read and run checks but never edit code; a researcher should
never write. If a sub-agent keeps the full default toolset, a "read-only" role is only a
polite request, not a guarantee. You need a hard allow/deny, not an instruction.

**P4. Which files and folders may it read?**
A fresh sub-agent can, by default, read any path its tools can reach — including files far
outside its job. You need to be able to confine reads to a defined working area, so an agent
cannot wander the filesystem (or the rest of the repo) for context it should not have.

**P5. Can it be stopped from reading secrets?**
A special case of P4 with real blast radius: nothing should let *any* agent read `.env`
files, private keys, credentials, or `~/.ssh/`. This guardrail must apply regardless of the
agent's role or how it tries (Read tool, `cat` via Bash, grep, …).

**P6. Can two agents in the same workflow have *different* access?**
Isolation is often role-specific. Example: an "algorithm-blind" test-writer must be unable
to read the internal design file, while the reviewer and implementer in the *same* run must
be able to. You need per-agent access rules, keyed to which agent is calling.

**P7. Can it be prevented from causing side effects outside its lane?**
An agent that writes code or runs commands can corrupt the shared working tree. You need the
option to give an agent its own isolated working copy, and/or a read-only mode, so its
actions cannot leak into everyone else's state.

**P8. How do you know what it actually did?**
A sub-agent's work happens in a separate context you don't see. To trust, tune, and audit
the system you need a record: which model it used, how many tokens it burned, and — for
security and correctness — exactly which files it read, attributed to the specific agent.

**P9. How does a fresh-context agent get what it needs?**
A sub-agent has no memory of the parent conversation. Whatever it needs must be handed to it
explicitly. The risk is either starving it (it flails or re-derives) or over-sharing (it
sees context that biases it, defeating the point of isolation).

**P10. Will it launch reliably, and by what name?**
Agents can be defined in several places (project, user, plugin), addressed by different
names, and behave differently in interactive vs headless runs. You need to know how an agent
is discovered, how it is addressed, and which configuration actually takes effect at runtime.

---

## Part 2 — How each goal is achieved

Sub-agents are configured mainly through an **agent-definition file** — a Markdown file with
YAML frontmatter (in `.claude/agents/` for a project/user, or a plugin's `agents/`
directory) whose body is the reusable brief. Cross-cutting file/secret rules are enforced
with a **PreToolUse hook**. The mechanisms:

### P1 — Model → `model:` frontmatter (or inline at spawn)
Set `model:` in the agent definition. It can also be overridden per-invocation by the
Task/Agent tool's `model` parameter. Resolution order: per-invocation parameter → agent-def
`model:` → environment default → parent session's model. Pin it in the definition so the
role's model is stable and versioned; override inline only for one-off experiments.

```yaml
---
name: code-reviewer
model: opus        # reviewer runs on a stronger model than the implementer
---
```

### P2 — Effort → `effort:` frontmatter (only there)
Declare `effort:` (`low` | `medium` | `high` | `xhigh` | `max`) in the agent definition.
**There is no spawn-time override for effort** — if it is not set in the definition, the
sub-agent inherits the parent's effort. So effort is pinned *only* through the agent-def
file. Pair it with the model to express "design & reviews think harder than implementation."

```yaml
---
model: sonnet
effort: high
---
```

### P3 — Tools → `tools:` (allowlist) / `disallowedTools:` (denylist), hard-enforced
List the exact tools the agent may use, or the ones it may not. These are **hard
restrictions** enforced at the tool-call level — a denied tool is not merely discouraged, it
is unavailable. This is how a read-only reviewer is *made* read-only.

```yaml
---
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit     # reviewer cannot modify anything
---
```

### P4 — Read confinement → a working-directory fence
Enable `permissions.blockReadsOutsideWorkingDirectories` to hard-block **both** the Read tool
and read-like Bash commands (`cat`, `grep`, `head`, …) on any path outside the working
directories. Stage the agent's inbox inside its working area and keep everything else out.
This is a session-level, all-or-nothing fence — use it when an agent should see only its own
folder.

```json
{ "permissions": { "blockReadsOutsideWorkingDirectories": true } }
```

### P5 — Secrets protection → a PreToolUse guard hook
Ship a **PreToolUse hook** (matching `Read|Bash|Grep|Glob`) that inspects the target path and
**denies** anything matching `.env`, private keys, `credentials`, `~/.ssh/`, etc. — for every
agent, however it tries. A hook that exits with a "deny" decision blocks the call before it
runs. Because the guard is central, the rule is maintained in one place and applies
everywhere.

### P6 — Per-agent access → the same hook, keyed on `agent_type`
The PreToolUse hook receives, on stdin, an **`agent_type`** (and `agent_id`) identifying which
agent is making the call. Branch on it: deny a specific file for one role while allowing it
for others. This is how an algorithm-blind test-writer is denied the internal design file
while the reviewer and implementer are not — enforced, not merely asked.

```python
# inside the guard hook (sketch)
if "test-writer" in agent_type and "design-internal" in target:
    deny("the test-writer is algorithm-blind and must not read the internal design")
```

Ship the hook **with the plugin** (a `hooks/hooks.json` referencing
`${CLAUDE_PLUGIN_ROOT}/…`) so it is active whenever the plugin is, and pair it with a role
instruction in the agent's body for **defense-in-depth** (the agent declines on its own; the
hook is the backstop).

### P7 — Side-effect isolation → `isolation: worktree` and/or `permissionMode: plan`
Set `isolation: worktree` to run the agent in its own temporary git worktree (auto-cleaned if
it makes no changes; its shell commands are fenced to that worktree). Set
`permissionMode: plan` for a read-only posture. Note: a worktree is a *full* copy of the
branch — it does **not** hide a specific in-repo file; to keep a file from an agent, keep the
file out of its working area (P4) or deny it in the hook (P6).

```yaml
---
isolation: worktree
permissionMode: plan
---
```

### P8 — Observability → a hook audit log + the session transcript
- **What it read (audit):** have the PreToolUse hook append one record per tool call —
  `{ts, agent_type, agent_id, tool, target}` — to a run-log. This is the stable, attributable
  record of every read, per agent.
- **Model & tokens:** the session transcript (JSONL under
  `~/.claude/projects/<project>/<session>.jsonl`) records the model and token usage per turn,
  including sub-agent side-transcripts. Treat this as a **best-effort** source: the format is
  internal and can change between releases, so parse defensively and prefer the hook log for
  anything you must rely on.

### P9 — Context handoff → curated files + a self-sufficient brief
Because the agent has no memory of your conversation, hand it a **curated inbox of files** and
a brief that names exactly what to read and do. Pass durable artifacts (a spec, a test plan)
by path rather than pasting the whole conversation — files are the single source of truth and
let you *choose* what the agent sees (which is also what makes selective isolation, P6,
possible). Give it everything it needs and nothing that would bias it.

### P10 — Discovery, naming & reliability
- **Definition scope & precedence:** project `.claude/agents/` → user `~/.claude/agents/` →
  plugin `agents/`. A project/user definition is picked up in a **fresh** session (it does not
  hot-reload mid-session).
- **Naming:** a plugin's agents are addressed by a **namespaced** `subagent_type`,
  `plugin-name:agent-name` (e.g. `implement-feature:test-writer`) — not the bare name.
- **Runtime reliability:** configuration that must always take effect (especially hooks)
  should be **shipped with the plugin** or placed in **user settings**; a project
  `.claude/settings.json` may not apply in headless (`claude -p`) runs. **Verify the runtime
  behavior**, don't assume it from configuration.

---

## Part 3 — Quick reference

| Goal | Mechanism | Where configured |
|------|-----------|------------------|
| P1 Model | `model:` (+ inline `model` param) | agent-def frontmatter / spawn call |
| P2 Effort | `effort:` (no inline override) | agent-def frontmatter only |
| P3 Tool allow/deny | `tools:` / `disallowedTools:` (hard) | agent-def frontmatter |
| P4 Read confinement | `blockReadsOutsideWorkingDirectories` | settings `permissions` |
| P5 Secrets guardrail | PreToolUse hook (deny .env/keys) | plugin `hooks/hooks.json` |
| P6 Per-agent access | PreToolUse hook keyed on `agent_type` | plugin `hooks/hooks.json` |
| P7 Side-effect isolation | `isolation: worktree`, `permissionMode: plan` | agent-def frontmatter |
| P8 Audit / attribution | hook audit log (+ transcript for model/tokens) | plugin hook / transcript |
| P9 Context handoff | curated files + self-sufficient brief | conductor / spawn brief |
| P10 Discovery & naming | scope precedence; `plugin:agent` name; ship hooks | plugin / user settings |

---

## Part 4 — Hard-won rules (gotchas)

1. **Effort cannot be set at spawn time** — only in the agent definition. Pin it there.
2. **Ship hooks with the plugin (or in user settings).** A project-settings PreToolUse hook
   can silently fail to fire in headless runs; plugin hooks fire for the conductor *and* its
   sub-agents.
3. **Plugin agents are namespaced** (`plugin:agent`). The bare name will not resolve.
4. **A worktree does not hide files** — it is a full branch copy. Confine reads (P4) or deny
   in the hook (P6) to keep a file from an agent.
5. **Tool allow/deny does not confine file *reads*.** `disallowedTools: Write` stops writing,
   not reading; use the fence (P4) or the hook (P5/P6) for read control.
6. **Don't rely on parsing the transcript** for anything critical — the format is internal
   and unstable. The hook audit log is the dependable record.
7. **Fresh context is total** — the sub-agent knows only what you pass. Put it in files.
8. **Verify at runtime.** Documentation and defaults can differ from actual behavior; confirm
   model, tool blocks, and hook firing empirically before you depend on them.

---

## Part 5 — Launch checklist

Before spawning a sub-agent, decide and encode:

- [ ] **Model** and **effort** for the role (reviews/design ≥ implementation).
- [ ] **Tools** it may use; explicitly **deny** the rest (read-only for critics).
- [ ] **Read access** — which folder is its lane; is the fence needed?
- [ ] **Secrets** — is the guard hook active for `.env`/keys?
- [ ] **Role-specific denials** — any file this agent (by `agent_type`) must not read?
- [ ] **Side effects** — does it need `isolation: worktree` / read-only mode?
- [ ] **Handoff** — the curated inbox files and a self-sufficient brief.
- [ ] **Observability** — is every read logged and attributed; can you see model/tokens?
- [ ] **Naming** — correct namespaced `subagent_type`; definition present in a fresh session.
