# Finding: a dated subagent model pin (`claude-opus-4-8`) is NOT honored in the dev container

**Date:** 2026-09-11 · **Branch:** `refactor/shippable-plugin` · **Status:** open (root-cause
check deferred until the in-flight Phase 4 run finishes, then run the checks in §5).

Feeds the Developer Guide's **model-pinning ADR** (Phase 3), alongside
[`isolation-experiments.md`](./isolation-experiments.md).

---

## 1. What we observed

The two reviewer gates are pinned to the **explicit dated ID** `claude-opus-4-8` in their
agent defs (commit `e093182`):

- `implement-feature-plugin/agents/test-reviewer.md` → `model: claude-opus-4-8`
- `implement-feature-plugin/agents/code-reviewer.md` → `model: claude-opus-4-8`

But in the Phase 4 container run (`00-async-cached-json-fetcher-202609110808`, session
`fba1dac5`), **every reviewer spawn actually ran `claude-opus-5`, not `claude-opus-4-8`.**

## 2. Ground-truth evidence (not the conductor's self-report)

The conductor's `handoff/run-log.jsonl` `model` field is **hand-written by the conductor** — a
belief, not proof. Ground truth is each subagent transcript's `message.model` field
(`~/.claude/projects/<slug>/<session>/subagents/agent-*.jsonl`, typed by `.meta.json`
`agentType`):

| Gate | agentType | Pinned in agent def | **Actually ran** |
|---|---|---|---|
| WRITE-TESTS ×3 | `implement-feature:test-writer` | `sonnet` (alias) | claude-sonnet-5 |
| IMPLEMENT ×2 | `implement-feature:implementer` | `sonnet` (alias) | claude-sonnet-5 |
| VERIFY ×2 | `implement-feature:verifier` | `sonnet` (alias) | claude-sonnet-5 |
| **TEST-REVIEW ×3** | `implement-feature:test-reviewer` | **`claude-opus-4-8`** | **claude-opus-5** |
| **CODE-REVIEW ×2** | `implement-feature:code-reviewer` | **`claude-opus-4-8`** | **claude-opus-5** |

The `sonnet`-alias gates resolved correctly (latest Sonnet). Only the **dated Opus ID** did not
stick — it landed on the latest available Opus instead.

## 3. What the docs say (model resolution)

Per the official [model-config docs](https://code.claude.com/docs/en/model-config), the subagent
model is resolved highest-wins:

1. Per-invocation `model` passed to the Agent tool
2. **Subagent frontmatter `model:`** ← our `claude-opus-4-8` lives here (rank 2)
3. `CLAUDE_CODE_SUBAGENT_MODEL` env var
4. Session model
5. Account default

The frontmatter field **explicitly accepts a full dated ID** (`claude-opus-4-8` is the docs'
own example), so our **syntax is correct** — the failure is downstream of the pin, not the pin
itself.

## 4. Most likely cause

The docs describe **automatic fallback**:

> When a requested model is excluded by `availableModels` or other restrictions, Claude Code
> substitutes a fallback model automatically rather than failing.

Because the **sonnet** gates ran their pinned sonnet fine and only the **dated Opus ID** slid to
the available Opus (`claude-opus-5`), the leading hypothesis is that **`claude-opus-4-8` is not
available to the container's Claude account**, so it fell back to the nearest available Opus.
**No config can force a model the account cannot access.**

Second trap to rule out: [GitHub issue #10993](https://github.com/anthropics/claude-code/issues/10993)
reports that **`CLAUDE_CODE_SUBAGENT_MODEL`, when set, always overrides the frontmatter `model:`**
(contradicting the documented order; closed "not planned"), full model names only. A
[field report by Thomas Witt](https://www.thomas-witt.com/blog/blog-subagent-model-pin/) documents
the frontmatter pin "silently dropping through" to the session model across releases — but ours
stayed *Opus*, not the *session* Sonnet, so that variant is less likely here.

## 5. How to force `claude-opus-4-8` — and the checks to run after the run

Ranked options (from the docs + issue):

1. **Frontmatter `model: claude-opus-4-8`** — already in place; recommended, self-documenting,
   scoped to one agent. Not sticking ⇒ fix is downstream.
2. **Confirm availability + no override** — ensure `claude-opus-4-8` is in the account's
   `availableModels` (not excluded) and that **`CLAUDE_CODE_SUBAGENT_MODEL` is unset**.
3. **`ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8`** — pins what the Opus tier/alias resolves to;
   good complement if the dated ID is being coerced to "latest Opus."
4. **Avoid `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-8`** for our case — blunt; forces **every**
   subagent (incl. the Sonnet gates) onto Opus 4.8. Full model name only.

**Deferred checks (run in the container after Phase 4 completes):**
- [ ] `env | grep -Ei 'CLAUDE_CODE_SUBAGENT_MODEL|ANTHROPIC_.*MODEL'` — is anything overriding?
- [ ] Is `claude-opus-4-8` actually offered to the container's account (available-models list /
      `availableModels` restriction)?
- [ ] Try `ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8` and re-run a reviewer gate; re-check the
      subagent transcript's `message.model`.
- [ ] Decide the product's stance: (a) accept "reviewers = latest Opus" and **correct the
      now-false SKILL.md claim** ("reviewer rows always read `claude-opus-4-8`"), or (b) keep the
      dated pin only if it's provably honored on a real end-user install.

## 6. Consequences to fix (post-decision)

- Commit `e093182`'s reproducibility goal (a dated reviewer version) is **not achieved** in this
  environment — the dated pin behaves like the `opus` alias (→ latest Opus).
- The Gate 0 SKILL.md note from commit `133025c` currently **overclaims** ("the two reviewer rows
  always read `claude-opus-4-8`, never the `opus` alias") — **empirically false**; correct it once
  §5 settles the root cause.

## Sources

- [Model configuration — Claude Code Docs](https://code.claude.com/docs/en/model-config)
- [Issue #10993 — subagent model selection & `CLAUDE_CODE_SUBAGENT_MODEL`](https://github.com/anthropics/claude-code/issues/10993)
- [Subagent Frontmatter — Developers Digest](https://www.developersdigest.tech/guides/subagent-frontmatter)
- [Subagent model pinning field report — Thomas Witt](https://www.thomas-witt.com/blog/blog-subagent-model-pin/)
