# Reading order for a full repo review

Goal: onboarding (understand current state + rationale) **and** technical audit
(scrutinize the plugin/hook implementation), covering every substantive file.
Trivial manifests are skipped (listed at the end) unless something upstream flags
one of them for a closer look.

## Phase 1 — Narrative context (why this exists, where it stands)
1. `CLAUDE.md` — repo orientation for Claude Code sessions.
2. `README.md` — repo map, one-paragraph pitch.
3. `RESUME.md` — live progress tracker; where the tutorial stands right now.
4. `PLAN.md` — the full 21-chunk plan, the 11-gate product design, change-of-direction log.
5. `TUTORIAL.md` — accumulated concept reference + captured Q&A.
6. `PATTERNS.md` — design-patterns/anti-patterns/traps checklist (P1, P15, … — referenced elsewhere).

## Phase 2 — The isolation mechanism (load-bearing empirical claim)
7. `design/isolation-experiments.md` — the experiments.
8. `LAUNCHING-SUBAGENTS.md` — report distilling what's proven vs. best-effort (references the experiments doc).

## Phase 3 — The toy plugin (warm-up on plugin mechanics)
9. `toy-greet-plugin/commands/greet.md`
10. `test-toy-greet-plugin/README.md` — how it's exercised.

## Phase 4 — The real product, `implement-feature-plugin` (critical read — audit target)
11. `implement-feature-plugin/commands/implement-feature.md` — thin command entry point.
12. `implement-feature-plugin/skills/implement-feature/SKILL.md` — the conductor's full score.
13. `implement-feature-plugin/skills/implement-feature/references/quality-standards.md` — single source of truth for "green"/coverage/mutation gates.
14. Templates together (interface/internal split mechanism):
    - `references/requirements-template.md`
    - `references/design-interface-template.md`
    - `references/design-internal-template.md`
    - `references/test-plan-template.md`
15. `implement-feature-plugin/agents/*.md`, in gate order: `test-writer.md` → `test-reviewer.md` → `implementer.md` → `verifier.md` → `code-reviewer.md`. Cross-check each against its inbox/outbox in `SKILL.md`.
16. `implement-feature-plugin/hooks/hooks.json` + `implement-feature-plugin/hooks/scripts/guard.py` — the enforcement code; check it against the four claims in `SKILL.md`'s Observability section.
17. `implement-feature-plugin/toolchain/requirements-dev.txt` — cross-check versions against `quality-standards.md` and the Dockerfile.

## Phase 5 — Environment (skim, not deep audit)
18. `.devcontainer/Dockerfile` + `.devcontainer/devcontainer.json` — sanity-check toolchain install matches `requirements-dev.txt` and the guard hook's env-var expectations (`CLAUDE_PROJECT_DIR`).
19. `DEVCONTAINER.md` — only if planning to actually run the container.

## Skipped (bare manifests, no design decisions inside)
- `.claude-plugin/marketplace.json`
- `implement-feature-plugin/.claude-plugin/plugin.json`
- `toy-greet-plugin/.claude-plugin/plugin.json`
- `.devcontainer/devcontainer-lock.json`
- `.gitignore`

Revisit one of these only if a Phase 4 finding makes it relevant (e.g. namespacing
in `plugin.json` vs. the `subagent_type` strings used in `SKILL.md`).
