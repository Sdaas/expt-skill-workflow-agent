# Refactor Plan — Tutorial repo → shippable `implement-feature` plugin

**Branch:** `refactor/shippable-plugin`. **Authorship:** Soumendra Daas <soumendra.daas@gmail.com>.

This plan is the source of truth AND the resume pointer for the refactor. Execution model is
**phase-boundary relaunches** (grilling decision Q11-B, 2026-09-10): one session per phase, each reads
this file, executes its phase, updates §5, commits. Between phases the user relaunches a fresh session.

---

## 0. CURRENT STATE — read this first on resume

- **Phase 0: DONE** (branch created, CLAUDE.md retired on `main`, scratch dir deleted, issues triaged
  & labelled, progress tracker added).
- **NEXT: Phase 1** — the 9 pile-1 code fixes, dependency-ordered, starting with **#10 (workdir
  redesign)**. See §4 Phase 1 and §5 for the running checklist.
- **Model note:** Phase 1 is deep interdependent surgery on `SKILL.md` + `guard.py` + `analyzer/` +
  templates — run it on a high-capability model / high effort.
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

### Phase 1 — Pile-1 fixes — ⬜ NOT STARTED
- [ ] #10 + #17 — per-feature artifact/handoff dir, numbered files, single-run lock
- [ ] #11 — STOP gates present the real artifact (draft → revise → promote)
- [ ] #8 — triviality assessment + branch recommendation; never commit on main
- [ ] #5 — kill reference-file read-tax
- [ ] #16 (+#1) — secret false-positive on Bash strings; drop dead basename block
- [ ] #12 — confine the test-reviewer
- [ ] #15 — analyzer reads `<uuid>/subagents/*.jsonl`
- [ ] #13 — mutation kill-rate anchored at 80%
- [ ] #14 — post-run analysis command + auto-report + pre-Gate-9 breach warning
- [ ] guard + analyzer unit tests green in container

### Phase 2 — First container dry run (`parse_duration`) — ⬜ NOT STARTED

### Phase 3 — Docs restructure (README router + UG + DG + Tutorial) — ⬜ NOT STARTED

### Phase 4 — Second feature (file-I/O + async-REST + fault injection) + dry run — ⬜ NOT STARTED

### Phase 5 — Merge prep + merge to `main` — ⬜ NOT STARTED

---

## 6. Open risks / watch-items
- **Toolchain on a real machine** (Q10): v1 documents manual install + relies on Gate-0 hard-fail with
  an actionable message. Auto-install is v1.1.
- **#10 workdir redesign** is the riskiest fix — it touches the handoff contract every gate depends on.
  Do it first and re-run guard/analyzer tests immediately.
- **Install-from-GitHub mechanics** need a real in-container verification during Phase 2/3 (marketplace
  add from a git URL, then install) — treat as a fact to confirm, not assume.
