# Refactor Plan — Tutorial repo → shippable `implement-feature` plugin

**Branch:** `refactor/shippable-plugin`. **Authorship:** Soumendra Daas <soumendra.daas@gmail.com>.

This plan is the source of truth AND the resume pointer for the refactor. Execution model is
**phase-boundary relaunches** (grilling decision Q11-B, 2026-09-10): one session per phase, each reads
this file, executes its phase, updates §5, commits. Between phases the user relaunches a fresh session.

---

## 0. CURRENT STATE — read this first on resume

- **Phase 0: DONE** (branch created, CLAUDE.md retired on `main`, scratch dir deleted, issues triaged
  & labelled, progress tracker added).
- **Phase 1: DONE 2026-09-10** — all 9 pile-1 fixes landed across 8 logical commits
  (#10+#17+#11, #8, #5, #16+#1, #12, #15, #13, #14). SKILL.md rewritten for the new artifact-dir /
  numbered-handoff / draft→promote / branch-decision / analytical-review workflow; guard.py gained
  pointer-file run-log resolution, draft-confinement, path-aware tool-split secret detection, and
  reviewer write-confinement; analyzer gained `--workdir`, subagent-transcript reading, and a 5th
  detective check; new `commands/analyze-run.md`. **52 unit tests green on host** (pytest-only).
  Patterns P44–P55 in PATTERNS.md.
- **Phase 2: FIRST DRY RUN DONE + triaged 2026-09-10** — `/implement-feature parse_duration` ran
  end-to-end in the container (all gates → real commit on `feature/00-parse-duration`). **All
  invariants held** (isolation 5/5, model pinning Opus5-reviews/Sonnet5-impl transcript-proven,
  lock lifecycle, draft→promote, typed repair loop, 304 tests / 100% cov / mutation 99.2%). Five
  triage items handled: two guard false-positives (`2>&1`→`&1`, `/dev/null`), P56 conductor-model
  self-check, (a) gitignore the `if-runlog.jsonl` fallback, (b) P57 smallest-viable scope anchor.
  See §5 Phase 2 for detail. **58 unit tests green on host.**
- **Phase 2 (ii): DONE 2026-09-11** — the confirming minimal `slugify` dry run ran green
  (P56+P57 confirmed live; 5/5 isolation after the heredoc fix). Five fixes + 2 backlog issues
  landed this session; see §5 Phase 2 (ii). **Host: 65 unit tests green.**
- **Phase 4: STARTED 2026-09-11, NOT YET COMPLETE.** Chose Phase 4 first (per the §0 recommendation).
  Fixture `~/test-implement-feature` bootstrapped for it (`webcache` src-layout pkg, `httpx`,
  `asyncio_mode=auto`). Ran `/implement-feature` end-to-end (gates 0→11) for the **async cached
  JSON fetcher** feature (`CachedFetcher`), ending in a **real commit `7047829`** on
  `feature/00-async-cached-json-fetcher` (never on `master`). Three fixes landed on the branch
  during/after this run — see §5 Phase 4 for detail:
  - Gate 0 STOP-summary restyle (concise, deviation-focused house convention). Commit `3df406f`.
  - Non-importable project package caught before it fakes a TDD red (`pip install -e .` gap in the
    fixture produced a false RED). Commit `3257786`.
  - Stale Gate 0 note fixed (reviewers pin the explicit `claude-opus-4-8`, not the `opus` alias).
    Commit `133025c`.
  - **✅ RESOLVED FINDING** (`design/model-pinning-findings.md`, closed 2026-09-11): the dated
    reviewer pin `claude-opus-4-8` **IS honored.** Re-audited all four sessions' raw subagent
    transcripts (`message.model` per `agentType`). Root cause of the earlier confusion: the two
    write-ups audited **different runs** in a reused project dir. The pin landed 2026-09-11
    03:44 UTC (`e093182`); every **post-pin** session (incl. the committed Phase 4 run session
    `251d3474`) ran reviewers on `claude-opus-4-8`, while the two Sep-10 **pre-pin**
    `parse_duration` sessions correctly used the `opus` alias → `claude-opus-5`. No override env
    var; not a fallback. The Gate 0 SKILL.md note (`133025c`) is **correct as written** — no
    edit needed. Evidence table + the "tie session→run via feature/workdir/SHA before trusting
    it" lesson are carried into the Phase 3 ADR.
  - **Fault-injection pass (timeouts, 5xx) has NOT been run yet** — Phase 4's "done" bar is two
    things: a green dry run (✅ done) AND the fault-injection pass against the un-mocked VERIFY
    gate (❌ not started). Phase 4 is therefore **not complete**.
  - The container fixture (`~/test-implement-feature`) has small **uncommitted** local tweaks
    (`.claude/settings.json`, `.gitignore`, 3 lines total) from this run — check `git diff` there
    before continuing; harmless either way since the fixture is ephemeral.
  - Container `vibrant_kapitsa` (volume `expt-skill-workflow-claude`) was left **running** (not
    torn down) with these artifacts intact — no need to re-bootstrap the fixture to resume.

- **NEXT (resume here), in order:**
  1. ✅ DONE — model-pinning re-audit complete: pin IS honored, `design/model-pinning-findings.md`
     closed, SKILL.md note confirmed correct (no edit).
  2. Run the **fault-injection pass** (network timeouts, 5xx) against the async fetcher feature to
     actually finish Phase 4. **Mechanism decided: `httpx.MockTransport`** (deterministic, no
     network/extra process, fits the pinned toolchain).
  3. Then **Phase 3** (docs) — README router + UG + DG + Tutorial, absorbing PATTERNS/TUTORIAL/etc.
     per §3 doc-fate map, describing the now-finished reality.

  **Dry-run mechanics (confirmed, see memory `phase2-dryrun-mechanics`):** the container's
  directory-source marketplace loads the plugin **from the workspace**
  (`/workspaces/expt-skill-workflow-agent/implement-feature-plugin/**`), **not** the
  `~/.claude/plugins/cache/...` copy (that copy is vestigial — 9/9 plugin-file reads in the (ii)
  dry run came from the workspace, 0 from the cache). **No rsync/cache-sync step is needed** — a
  workspace edit takes effect after a **session restart** (SKILL/agents load at startup; the
  guard hook reloads per tool call). Fixture repo: container `~/test-implement-feature`
  (ephemeral, currently populated — see above). Host test harness: recreate `/tmp/if-venv.tmp`
  (`python3 -m venv` + `pip install pytest`); full toolchain (ruff/mypy/mutmut) only runs
  in-container. Still to confirm live: install-from-GitHub mechanics (a real end-user install
  would hit the cache path, not the workspace path — UG must document that distinction).
- **Model note:** Phase 1 was deep interdependent surgery on `SKILL.md` + `guard.py` + `analyzer/` +
  templates — run on a high-capability model / high effort.
- **Dry runs (Phases 2, 4):** the USER drives the interactive `/implement-feature` in a container
  terminal (TTY constraint); the session only analyses the resulting `if-runlog.jsonl` + transcripts
  and fixes fallout on the branch.

### Resume prompt (paste at the start of each new session)
> Read `REFACTOR-PLAN.md` (on branch `refactor/shippable-plugin`) — §0 CURRENT STATE and §5 progress
> log tell you where we are. Continue with the next unstarted phase. Follow the phased plan; commit
> per logical unit; update §5 as you go. Do not revert to the old paced-tutorial workflow.

### Still-open plan decisions (defaults chosen; override anytime)
- **docs/ layout:** `docs/user-guide.md`, `docs/developer-guide.md`, `docs/tutorial.md` (default).
- **All fixes before docs:** yes — Phase 1+2 precede Phase 3 (taken as approved: "plan looks good").
- **#14 in v1:** folded in (default; easiest single item to cut for a leaner v1).

---

## 1. Goal (settled via grilling, 2026-09-10)

Convert this repo from a **paced learning exercise** into a **genuinely usable** plugin a stranger can
install from GitHub and run against their own Python repo — organized as **one repo** with a top-level
README that routes **three audiences**:

- **(a) User Guide (UG)** — install from GitHub, Python-only setup + toolchain prerequisite, how to run,
  FAQ. Targets a real user on their **own machine / own repo**.
- **(b) Developer Guide (DG)** — architecture, gate design, agent-def files, the guard hook, the
  analyzer, **ADRs**, and the **testing / dry-run methodology**. Targets someone improving the plugin.
  The **design-principles section absorbs ALL of `PATTERNS.md`** — not just the best-practice patterns
  but the **anti-patterns and traps** too (what NOT to do, and the mistakes that bit us).
- **(c) Tutorial** — concepts (plugin vs command vs skill vs workflow) and **subagent isolation**
  (folds in `LAUNCHING-SUBAGENTS.md` + `design/isolation-experiments.md`), with `toy-greet-plugin/` as
  the runnable example. Reading order for a new dev: **c → b → a**.

### Definition of "done" / shippable (the verification bar)

- **A green end-to-end dry run IN THE CONTAINER** is the gate — not "docs exist."
- Run `/implement-feature` through **all gates** on a **bootstrapped Python repo**, ending in a **real
  commit**, with **no manual workarounds** (so #11 and #10 must already be fixed).
- **Two features**, to exercise more than the happy path:
  1. `parse_duration(s) -> int` (pure function) — the minimal happy path.
  2. A feature that does **file I/O + an async REST call** to a well-known public JSON API. The dry run
     then **injects faults** — network timeouts, 5xx responses — so the un-mocked VERIFY gate, the
     resiliency/reliability review dimension, and the concurrency policy all get genuinely exercised,
     not just asserted.
- The container is **our** test harness. A **real user runs on their own machine against their own
  repo** — which is exactly why branch-safety (#8) is a pile-1 blocker.

### Process

- **plan → approve → phased execution** on the branch. The paced one-chunk-at-a-time "next" cadence is
  **retired** for this work.
- Commit per **logical unit** (not per 250-word chunk). **Keep** the existing git history (honest
  provenance).
- **v1 scope is deliberately minimal-but-real**: it works, it's honest about prerequisites, it's
  documented. Automation and conveniences are explicitly deferred to v1.1 (see backlog).

---

## 2. Issue triage (all 18 open issues)

### Pile 1 — Fix BEFORE docs (run-blockers / change what the docs would say)
| # | Title | Touches |
|---|---|---|
| #10 | workdir ↔ repo-root collision + single-run lock (code stays in repo, isolation via git) | SKILL.md, guard.py |
| #17 | numbered handoff files (`01-requirements.md`, …) — done alongside #10 | SKILL.md, templates |
| #11 | human reviews the **real artifact** (draft → review/revise → promote), not a summary | SKILL.md |
| #8  | Gate assesses triviality → recommends branch vs current; **never commit on main** | SKILL.md |
| #5  | reference-file read-tax (inline hot-path + grant plugin-dir read) | guard.py, SKILL.md |
| #16 | secret false-positive on Bash command strings | guard.py |
| #12 | test-reviewer confinement (writes to scratchpad+outbox; analytical review only) | guard.py, agents/test-reviewer.md |
| #15 | analyzer blind to `<uuid>/subagents/*.jsonl` | analyzer/transcript.py |
| #13 | mutation kill-rate anchored at 80% + justification for deviation | quality-standards.md |

### Pile 2 — Fold INTO the refactor
| # | Title | Note |
|---|---|---|
| #6  | User Guide (UG) | **is** the refactor (Phase 3) |
| #7  | Developer Guide (DG) | **is** the refactor (Phase 3) |
| #14 | post-run analysis command (auto-report + standalone + pre-Gate-9 breach warning) | small; the observability payoff a real user wants; analyzer stays measure-only |
| #3  | PLAN gate-table exact filenames | resolved implicitly by the DG rewrite (PLAN.md is deleted) |

### Pile 3 — Defer to labeled backlog (v1.1+)
| # | Title | Disposition |
|---|---|---|
| #18 | committed regression harness (headless fixtures) | **fast-follow, v1.1** — "get it working first, then automate the hell out of it" |
| #9  | `/resume-feature` command | v2 (new command) |
| #1  | guard.py dead `looks_secret()` basename block | opportunistic cleanup (may fold into #16) |
| #2  | RESUME.md hardcoded/misspelled path | **moot** — RESUME.md is deleted |
| #4  | build the transcript analyzer | **verify & close as done** (built in chunk 20; residual = #15) |
| — | **NEW:** Gate 0 auto-installs the toolchain into the active venv | created in Phase 0 (Q10 v1.1 item) |

---

## 3. Doc-fate map

| File | Fate |
|---|---|
| `CLAUDE.md` | **Rewrite** → shippable-plugin orientation (early, so relaunch is safe) |
| `PLAN.md` | **Delete** |
| `RESUME.md` | **Delete** |
| `REVIEW-READING-ORDER.md` | **Delete** |
| `REFACTOR-PLAN.md` (this file) | Delete at merge (its content is transient) |
| `PATTERNS.md` | **Absorb** → DG "Design principles" section, then delete |
| `TUTORIAL.md` | **Absorb** → Tutorial (c), then delete |
| `LAUNCHING-SUBAGENTS.md` | **Absorb** → Tutorial (c) "subagent isolation" + DG, then delete |
| `design/isolation-experiments.md` | **Absorb** → DG (evidence behind the isolation ADR), then delete |
| `DEVCONTAINER.md` | **Keep** → referenced by DG (testing methodology) |
| `README.md` (root) | **Rewrite** → 3-audience router |
| `toy-greet-plugin/` | **Keep** → Tutorial's runnable example |
| `test-toy-greet-plugin/` | **Delete** (scratch ephemera) |
| `implement-feature-plugin/` | **Keep + fix** (the product) |
| `.claude-plugin/marketplace.json`, `.devcontainer/` | **Keep** |

### Proposed final top-level shape
```
README.md                      # pitch + router (User→UG, Developer→DG, Learner→Tutorial)
CLAUDE.md                      # rewritten: shippable-plugin orientation
docs/
  user-guide.md                # (a) install-from-github, python setup, toolchain, run, FAQ
  developer-guide.md           # (b) architecture, ADRs, design principles, guard hook, analyzer, testing
  tutorial.md                  # (c) concepts + subagent isolation + toy-greet walkthrough
DEVCONTAINER.md                # kept; linked from DG
implement-feature-plugin/      # the product
toy-greet-plugin/              # tutorial example
.claude-plugin/marketplace.json
.devcontainer/
```
(Tutorial may split into `docs/tutorial/` multi-file if it gets long — decided during Phase 3.)

---

## 4. Phases

### Phase 0 — Branch, safety, hygiene
- Create branch `refactor/shippable-plugin`; move this plan onto it.
- **Rewrite `CLAUDE.md`** to a minimal, accurate shippable-plugin orientation (retire the paced-tutorial
  rules) — done first so a relaunch mid-refactor is safe.
- Delete `test-toy-greet-plugin/`.
- Issue hygiene: create the **auto-install toolchain (v1.1)** issue; label the v1.1/v2 backlog (#18, #9,
  auto-install); verify & close **#4**; note **#2** as moot.
- Commit.

### Phase 1 — Pile-1 fixes (make it actually work) — dependency-ordered
1. **#10 + #17** — per-feature artifact/handoff dir with numbered files + single-run lock; code stays in
   the repo, gate isolation via git. (Foundational; everything else references the handoff dir.)
2. **#11** — STOP gates present the **real artifact** with a draft → review/revise → promote loop.
3. **#8** — triviality assessment + branch recommendation; **never commit on main**.
4. **#5** — kill the reference-file read-tax (inline hot-path guidance + grant plugin-dir read in guard).
5. **#16 (+#1)** — fix the secret false-positive on Bash strings; remove the dead basename block.
6. **#12** — confine the test-reviewer (writes to scratchpad+outbox only; analytical review, no
   reference impl / no mutmut at Gate 4).
7. **#15** — analyzer reads `<uuid>/subagents/*.jsonl` (real per-gate model/token split).
8. **#13** — anchor mutation kill-rate at 80% + require justification to deviate.
9. **#14** — post-run analysis command + auto-report after commit + pre-Gate-9 breach warning.
- Each fix keeps existing `guard`/`analyzer` unit tests green (run in container).
- Commit per fix (or tight cluster).

### Phase 2 — First container dry run (shake out Pile 1)
- Bootstrap a Python fixture repo in the container (pyproject + `src/` + `tests/`, git-init).
- Run `/implement-feature` on **`parse_duration`**, **no workarounds**; fix fallout; re-run to green.

### Phase 3 — Docs restructure (the three audiences)
- Write `README.md` router.
- Write `docs/user-guide.md` (UG, #6): install from GitHub via marketplace, Python-only prerequisite,
  **manual toolchain install** (`pip install -r implement-feature-plugin/toolchain/requirements-dev.txt`),
  Gate-0 preflight error explained, walkthrough, **FAQ**.
- Write `docs/developer-guide.md` (DG, #7): architecture (conductor + isolated gates), the 11-gate
  design, agent-def model/effort pinning, the guard hook, the analyzer, **ADRs** (isolation-via-plugin-
  hook, model pinning, interface/internal split, workdir redesign, …), **design principles** (from
  PATTERNS), and the **testing / dry-run methodology** (container).
- Write `docs/tutorial.md` (c): concepts + **subagent isolation** (fold LAUNCHING-SUBAGENTS +
  isolation-experiments) + `toy-greet` walkthrough.
- Delete/absorb per the doc-fate map. Resolve **#3** implicitly.

### Phase 4 — Second feature + final verification
- Add the **file-I/O + async-REST** feature; run its full dry run in the container to green, including
  the **fault-injection** pass (timeouts, 5xx) against the un-mocked VERIFY gate.
- **Two green dry runs = done.**

### Phase 5 — Merge prep
- Final `README.md` + `CLAUDE.md` pass; delete this `REFACTOR-PLAN.md`.
- Close every addressed issue with a commit reference.
- Merge `refactor/shippable-plugin` → `main`.

---

## 5. Progress log / phase checklist

Update this section as work proceeds — it is the resume anchor.

### Phase 0 — Branch, safety, hygiene — ✅ DONE 2026-09-10
- [x] Branch `refactor/shippable-plugin` created off `main`.
- [x] `CLAUDE.md` rewritten on `main` (paced-tutorial rules retired; points to branch + this plan). Commit `f44700a`.
- [x] `REFACTOR-PLAN.md` written + committed.
- [x] `test-toy-greet-plugin/` deleted.
- [x] Issue hygiene: created auto-install(v1.1) issue #19; labelled backlog (#9, #18, #19 → `v1.1`/`v2`); closed #4 (analyzer built ch.20; residual tracked in #15); #2 noted moot.
- [x] Two plan additions folded in: DG absorbs PATTERNS anti-patterns+traps (not just best practice); feature #2 = file-I/O + async-REST + fault injection.

### Phase 1 — Pile-1 fixes — ✅ DONE 2026-09-10
- [x] **#10 + #17 + #11** — per-feature artifact dir (`.implement-feature/<run>/`), numbered
  handoff files (`01-…`–`08-…`), `.active-run` pointer+lock, code-root/tests-root split,
  draft→promote review loop. SKILL.md rewritten; guard.py (pointer-file run-log resolution +
  deny subagent reads under `handoff/draft/`); all `agents/*.md` + `references/*-template.md`
  updated to numbered names + `<artifact_dir>`/`<code_root>`/`<tests_root>`; analyzer gains
  `--workdir`; `.gitignore` gets `.implement-feature/`. New `hooks/tests/test_guard.py`
  (9 tests). Patterns P47–P51 already in PATTERNS.md (captured ch.21); SKILL refs aligned.
  **25 unit tests green** (16 analyzer + 9 guard).
- [x] **#8** — Gate 0 branch decision: assess triviality → recommend stay vs new
  `feature/<NN-slug>`; hard never-on-default invariant (branch required if HEAD is
  default), human overrides triviality but not the guardrail; Gate 10 re-checks before
  commit. SKILL Gates 0/10; pattern P52. (Prose-only; no code.)
- [x] **#5** — reference-file read tax (P53). Part A: Gate 0 preflight reworded as
  explicitly **inline** (don't open quality-standards.md to run it); standards section
  documents the tax + fix. Part B: documented `permissions.allow` read rule for the plugin
  dir (install-time setting) — UG documents it for real users (Phase 3), dry-run fixture
  ships it in `.claude/settings.json` (Phase 2, where the exact glob is verified live).
  SKILL + PATTERNS P53. (Prose-only; no code.)
- [x] **#16 (+#1)** — path-aware, tool-split secret detection (P54). guard.py: `looks_secret(tool,
  target)` — Bash tokenizes (shlex, whitespace fallback) and flags only path-like secret tokens;
  other tools match by path component. Dropped the dead basename block (#1). analyzer/runlog.py:
  mirrored predicate + `read_calls` tracks `(tool, target)` so the detective check is tool-aware.
  Regression fixtures: benign `os.environ`/`secrets.token_hex`/etc. pass; real `cat .env` /
  `~/.ssh/id_rsa` / `credentials.json` / `.pem` denied. **39 tests green.** Pattern P54.
- [x] **#12** — test-reviewer confinement. guard.py rule 5: reviewer's only sanctioned
  writes are its handoff/ outbox + a scratch dir; Write/Edit and Bash write-redirections
  (`>`/`>>`/`tee`, best-effort) into the product tree are denied (P44 — disallowedTools is
  doc-only with Bash). agents/test-reviewer.md (D2): analytical review only, no reference
  impl, no mutmut (deferred to Gate 7), probes OK. SKILL Gate 4 updated. analyzer mirrors a
  5th detective check "test-reviewer stayed out of the product tree". **47 tests green.**
  Patterns P44/P45 already present.
- [x] **#15** — analyzer reads subagent transcripts (P51). transcript.py: `parse_subagents()`
  discovers `<main_stem>/subagents/*.jsonl`, attributes each via sibling `.meta.json`
  (best-effort key search, namespace stripped), folds per-model usage into the sidechain
  aggregate, and exposes a per-subagent breakdown. report.py renders the per-gate model
  split table. Extra-best-effort: missing/malformed subagents dir → empty, never raises.
  Fixtures added (`write_subagent`). analyzer/README updated (also covers C1/C4/C5 drift:
  `--workdir`, 5th verdict, tool-split secrets). **52 tests green.**
- [x] **#13** — mutation kill-rate anchored at 80% (P46). quality-standards.md documents
  the default anchor + deviation-justification + surface-at-approval; test-plan-template
  replaces bare `<M>%` with the 80% anchor + a justification line; SKILL Gate 2 tells the
  design agent to start at 80%, justify deviations, and surface the number for human veto.
  (Prose-only; no code.)
- [x] **#14** — observability wired in (P55). New `commands/analyze-run.md` standalone
  command; SKILL Gate 9 runs the fast isolation pass (`--no-transcript`) pre-approval and
  requires human acknowledgement on any VIOLATION; new Gate 11 REPORT auto-runs the full
  analyzer after commit. Analyzer stays measure-only (P40); reuses `--workdir`/`--no-transcript`
  (no new orchestration). CLAUDE.md gate count 0–11.
- [x] **guard + analyzer unit tests green** — 52 passed on the Mac host (pytest-only venv);
  full pinned-toolchain run (ruff/mypy/mutmut) is a container step for Phase 2.

### Phase 2 — First container dry run (`parse_duration`) — 🔶 RAN; triage in progress 2026-09-10
- **Ran** the full `/implement-feature` on `parse_duration` in the container against a fresh
  fixture repo (`~/test-implement-feature`), all gates 0→11, ending in a real commit on
  `feature/00-parse-duration`. **Invariants held:** isolation (5/5), model pinning
  (reviews=Opus 5, impl/tests=Sonnet 5, transcript-proven), lock created+cleared, draft→promote,
  typed →IMPLEMENT/→TESTS repair loop, 304 tests / 100% cov / ruff+mypy clean / mutation 99.2%.
- **Triage fixes landed this session (branch):**
  - `#12` reviewer write-detection false-flagged `2>&1` (parsed `&1` as a file) and `/dev/null`
    → guard + analyzer now drop `&`-fd-dups and allow `/dev/*`. Real run-log now 5/5 green.
  - `P56` — conductor ran on Sonnet, not the plan's Opus for INTERVIEW/DESIGN (a plugin can't
    pin its own session model). Added Gate-0 conductor model self-check + warn; corrected the
    stale "Opus 4.8" table naming (aliases resolve to latest tier). Effort left out of the
    report by decision (transcript model split suffices).
- **Observations — actioned:** (1) scope explosion → **fixed (b), P57** smallest-viable anchor at
  Gate 1 + template. (2) `if-runlog.jsonl` repo-root leak → **fixed (a)** Gate 0 gitignores it, P49.
- **Observations — logged, NOT fixed (cosmetic, decide later):** (3) workdir `run-log.jsonl` mixes
  guard-audit lines + conductor gate-summary lines (two schemas in one file since #10 pointed both
  there); the analyzer tolerates it but counts summary lines as empty-tool conductor calls. Options
  if we care: separate files again, or have the analyzer skip lines with a `gate` key.
- **Also noted:** feature 1 became `->float` (not the plan's `->int`) — fine, interview is the spec.
- Unit tests: **58 green on host**; `parse_duration` suite green in container (304 tests, 100% cov).

### Phase 2 (ii) — Second minimal dry run (`slugify`) — ✅ DONE 2026-09-11
- **Ran** `/implement-feature slugify` on a fresh minimal fixture (`~/test-if-minimal`,
  pure-python `textkit`), all gates 0→11, ending in a real commit on `feature/00-slugify`
  (never on `master` — #8 held). **P56 + P57 confirmed live** (conductor model self-check
  fired; Gate 1 anchored to smallest-viable, no scope explosion). Model split
  transcript-proven: reviews=**opus-5**, impl/tests/verify=**sonnet-5** (this run predates
  the 4.8 pin below). CODE-REVIEW converged after one `→TESTS` repair (missing `match=` on
  a `TypeError` message).
- **Findings + fixes landed this session (branch):**
  - **#5 read-tax is live-confirmed NOT silenced by the cache-path allow-rule** — the
    container's directory-source marketplace loads the plugin from the **workspace**
    (`/workspaces/…/implement-feature-plugin/**`), so the fixture's cache-path glob never
    matched. Fixtures patched with the workspace glob (container-only; a real GitHub install
    gets the cache path, which the UG will document).
  - **Cache-vestigial theory CONFIRMED** — the run-log shows **9/9 plugin-file reads from the
    workspace, 0 from the cache**. The rsync-into-cache ritual is unnecessary; workspace edits
    take effect after a session restart. (Memory `phase2-dryrun-mechanics` corrected.)
  - **Q1 — reviewer gates pinned to `claude-opus-4-8`** (explicit, not the floating `opus`
    alias). Commit `e093182`.
  - **Q2 — exception-message test-quality shifted left** of the mutation gate (standards +
    test-writer + test-reviewer + test-plan template). Commit `582d4a6`.
  - **Gate 11 report now persisted** to `<artifact_dir>/run-report.md` via a new analyzer
    `--out` flag (TDD). Commit `d719156`.
  - **Heredoc parser bug fixed** (guard + analyzer, TDD) — `bash_write_targets` parsed
    markdown `>` blockquotes inside heredoc bodies as redirections, which (a) made the guard
    DENY the reviewer's legit `cat > handoff/06.md <<EOF` write at runtime and (b) emitted a
    false isolation VIOLATION. Now strips heredoc bodies first; real (ii) run-log re-analyzes
    to **5/5, clean**. Commit `f87e46c`.
- **New backlog issues filed:** **#20** (parametrize homogeneous test-case families;
  v1.1/backlog), **#21** (clean-run harness: destroy + rebuild a fresh container per dry run;
  v1.1/backlog, overlaps #18).
- Unit tests: **65 green on host** (was 58 + 5 heredoc + 2 `--out`).

### Phase 3 — Docs restructure (README router + UG + DG + Tutorial) — ⬜ NOT STARTED

### Phase 4 — Second feature (file-I/O + async-REST + fault injection) + dry run — 🔶 IN PROGRESS 2026-09-11
- **Ran** `/implement-feature` for the async cached JSON fetcher (`CachedFetcher`) on
  `~/test-implement-feature` (`webcache` src-layout pkg, `httpx`, `asyncio_mode=auto`), all gates
  0→11, ending in a real commit `7047829` on `feature/00-async-cached-json-fetcher` (never on
  `master`). 243 tool calls, isolation 5/5 per the analyzer report.
- **Fixes landed:**
  - Gate 0 STOP-summary output-style restyle (glyph-led, terse happy path, deviations expanded
    once). Commit `3df406f`.
  - Non-importable project package caught before faking a TDD red — Gate 0 preflight now verifies
    `python -c "import <pkg>"`; Gate 3's RED exit-condition distinguishes a writer-correctable bad
    import from an environment `ModuleNotFoundError` (hard-stop, not re-spawnable);
    `test-writer.md` told not to report the latter as a valid red. Commit `3257786`.
  - Container Claude UX provisioned (status line, smart-rm hook, settings) via a devcontainer
    `postStartCommand` so a fresh volume self-heals. Commit `86325f3`.
  - Stale Gate 0 note fixed: reviewers pin the explicit `claude-opus-4-8`, not the floating `opus`
    alias (the restyle in `3df406f` had reintroduced the wrong claim). Commit `133025c`.
  - **Finding recorded** (`design/model-pinning-findings.md`, commit `69ace10`): claimed the dated
    `claude-opus-4-8` pin was not honored (ground truth said `claude-opus-5` actually ran) —
    **this session's direct re-check of the same run's transcripts contradicts that claim** (see
    §0 NEXT). **Unresolved — do not treat either document as settled.**
- **NOT done yet:** the fault-injection pass (timeouts, 5xx against the un-mocked VERIFY gate) that
  Phase 4's definition of done requires. Phase 4 is **not** a completed phase.
- Unit tests: 65 green on host (unchanged this phase; all fixes were prose/SKILL-only).

### Phase 5 — Merge prep + merge to `main` — ⬜ NOT STARTED

---

## 6. Open risks / watch-items
- **Toolchain on a real machine** (Q10): v1 documents manual install + relies on Gate-0 hard-fail with
  an actionable message. Auto-install is v1.1.
- **#10 workdir redesign** is the riskiest fix — it touches the handoff contract every gate depends on.
  Do it first and re-run guard/analyzer tests immediately.
- **Install-from-GitHub mechanics** need a real in-container verification during Phase 2/3 (marketplace
  add from a git URL, then install) — treat as a fact to confirm, not assume.
