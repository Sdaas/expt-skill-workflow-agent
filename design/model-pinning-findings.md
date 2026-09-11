# Finding: the dated reviewer pin (`claude-opus-4-8`) IS honored in the dev container

**Date:** 2026-09-11 · **Branch:** `refactor/shippable-plugin` · **Status:** ✅ RESOLVED
(re-audited from raw transcripts across all four sessions; earlier "not honored" claim was a
misattribution — see §5).

Feeds the Developer Guide's **model-pinning ADR** (Phase 3), alongside
[`isolation-experiments.md`](./isolation-experiments.md).

---

## 1. Conclusion (settled)

The two reviewer gates pin the **explicit dated ID** `claude-opus-4-8` in their agent defs
(commit `e093182`):

- `implement-feature-plugin/agents/test-reviewer.md` → `model: claude-opus-4-8`
- `implement-feature-plugin/agents/code-reviewer.md` → `model: claude-opus-4-8`

**The pin is honored.** In every session that ran *after* the pin landed, both reviewer gates'
subagent transcripts report `message.model = claude-opus-4-8` — including the committed Phase 4
async-fetcher run. The `sonnet`-alias gates resolve to `claude-sonnet-5` in every session. No
fallback, no coercion, no override env var. The Gate 0 SKILL.md note ("the two reviewer rows
always read `claude-opus-4-8`, never the `opus` alias", commit `133025c`) is therefore
**accurate as written** and needs no correction.

## 2. Ground-truth evidence (raw `message.model`, not the conductor's self-report)

Ground truth is each subagent transcript's `message.model` field
(`~/.claude/projects/<slug>/<session>/subagents/agent-*.jsonl`, typed by the sibling
`.meta.json` `agentType`) — **not** the conductor's hand-written `run-log.jsonl` `model` field.
The container's project slug `-home-vscode-test-implement-feature` accumulated transcripts from
**four** `/implement-feature` runs (the dir was reused across Phase 2 and Phase 4). The pin
landed **2026-09-11 03:44 UTC** (commit `e093182`). Reading every reviewer transcript directly:

| Session (start UTC) | Feature / phase | vs pin | Reviewer `message.model` | Sonnet gates |
|---|---|---|---|---|
| `c50fd39c` — Sep-10 03:01 | `parse_duration` (Phase 2) | **before** | `claude-opus-5` | `claude-sonnet-5` |
| `fba1dac5` — Sep-10 07:34 | `parse_duration` (Phase 2) | **before** | `claude-opus-5` | `claude-sonnet-5` |
| `c8d1ff00` — Sep-11 04:42 | partial (aborted) | **after** | `claude-opus-4-8` | `claude-sonnet-5` |
| **`251d3474` — Sep-11 08:07** | **`CachedFetcher` (Phase 4, commit `7047829`)** | **after** | **`claude-opus-4-8`** | `claude-sonnet-5` |

Every row is internally consistent: **before** the pin the reviewers used the floating `opus`
alias, which correctly resolved to the latest Opus (`claude-opus-5`); **after** the pin they ran
the dated `claude-opus-4-8`. There is no session in which the pin was in effect and *not*
honored.

Method (reproducible in-container):
```bash
BASE=~/.claude/projects/-home-vscode-test-implement-feature
for s in <session-uuids>; do
  for meta in "$BASE/$s"/subagents/*.meta.json; do
    grep -o '"agentType":"[^"]*"' "$meta"
    grep -o '"model":"[^"]*"' "${meta%.meta.json}.jsonl" | sort -u
  done
done
```

## 3. Model resolution (why the pin sticks)

Per the official [model-config docs](https://code.claude.com/docs/en/model-config), the subagent
model is resolved highest-wins:

1. Per-invocation `model` passed to the Agent tool
2. **Subagent frontmatter `model:`** ← our `claude-opus-4-8` lives here (rank 2)
3. `CLAUDE_CODE_SUBAGENT_MODEL` env var
4. Session model
5. Account default

The frontmatter field **accepts a full dated ID** (`claude-opus-4-8` is the docs' own example),
so the syntax is correct, and — confirmed below — nothing at ranks 1/3 overrides it in the
container.

## 4. Deferred checks — run, all clear

- [x] `env | grep -Ei 'CLAUDE_CODE_SUBAGENT_MODEL|ANTHROPIC_.*MODEL|CLAUDE_.*MODEL'` → **no
  model-override env vars set.** So the frontmatter pin (rank 2) is authoritative; the
  [issue #10993](https://github.com/anthropics/claude-code/issues/10993)
  `CLAUDE_CODE_SUBAGENT_MODEL`-always-wins trap does **not** apply here (the var is unset).
- [x] Is `claude-opus-4-8` actually offered to the container's account? **Yes — it ran**, in
  both post-pin sessions, so it is available and not excluded by `availableModels`.
- [x] Fallback substitution (docs: an unavailable model is swapped rather than failing) is
  **not** occurring for the reviewers — they land on the exact dated ID, not a substitute.

## 5. Why the earlier draft said the opposite (root cause of the confusion)

The first draft of this file (commit `69ace10`) concluded the pin was *not* honored. That was a
**misattribution**, not a real fallback failure. It identified the Phase 4 run as session
`fba1dac5` and reported its reviewers as `claude-opus-5`. But `fba1dac5` is a **Sep-10
`parse_duration` (Phase 2) run that predates the pin by a full day** — at that time the reviewers
were still the floating `opus` alias, so `claude-opus-5` was exactly correct. The **actual**
Phase 4 async-fetcher run (workdir `00-async-cached-json-fetcher-202609110808`, commit
`7047829`) is session **`251d3474`** (55 `CachedFetcher` refs, 100 workdir refs, 3 commit refs),
whose reviewers ran `claude-opus-4-8`. Once the run↔session mapping is correct, both the earlier
"opus-5" observation and the later "opus-4-8" observation are simultaneously true — of different
runs — and the pin comes out honored.

**Lesson (worth an ADR note):** always tie a transcript session to its run by grepping the
feature identity / workdir slug / commit SHA in the *main* transcript before reading its
subagents — a reused project dir mixes sessions from multiple runs, and mtime alone is not proof.

## 6. Consequences

- Commit `e093182`'s reproducibility goal (a dated reviewer version) **is achieved** in this
  environment.
- The Gate 0 SKILL.md note from commit `133025c` is **correct** — no edit needed.
- No product change required. Carry the §2 evidence table and the §5 lesson into the Phase 3
  model-pinning ADR.

## Sources

- [Model configuration — Claude Code Docs](https://code.claude.com/docs/en/model-config)
- [Issue #10993 — subagent model selection & `CLAUDE_CODE_SUBAGENT_MODEL`](https://github.com/anthropics/claude-code/issues/10993)
- [Subagent Frontmatter — Developers Digest](https://www.developersdigest.tech/guides/subagent-frontmatter)
- [Subagent model pinning field report — Thomas Witt](https://www.thomas-witt.com/blog/blog-subagent-model-pin/)
</content>
</invoke>
