# REVIEW.md — Review ledger

Instructions: see REVIEW-PROMPT.md. Read-only review; findings are append-only.

## Findings tracker & execution order

Ordered by priority (guarantee-breaking Majors first, then platform/doc Majors, then Minors, then
Nits). `superseded-by`/`downgraded-by` findings are listed but folded into their replacement's fix.
Action key: **FIX** = safe to fix directly in a small commit; **ISSUE** = file a GitHub issue (needs a
design decision, is multi-file/analyzer-level work, or is already tracked under Issue #22).

**Progress (2026-09-12):** Batch A (all 16 mechanical/doc + two guarded-tested code fixes: m-05
secrets-guardrail directory reads, m-06 confinement-path anchoring) is done — 16/30 rows checked
below; `python3 -m pytest implement-feature-plugin -q` is green (71 passed, incl. new regressions
for m-05/m-06). N-04 needed no action (already fixed by the repo-rename commit). Remaining: Batch B
(M-04, M-05 — the two guard Bash-bypass fixes) and Batch C/D (M-03, m-07/m-03, the Issue #22 cluster,
m-17) are still open, per the execution order below.

| # | ID | Sev | One-line | Action |
|---|----|-----|----------|--------|
| 1 | [ ] M-04 | Major (guarantee) | Test-integrity guard has no `Bash` defense — implementer can `sed -i`/heredoc a test file undenied | **FIX** |
| 2 | [ ] M-05 | Major (guarantee) | Algorithm-blind guard is a literal filename match — `cat handoff/*.md` leaks internal design to test-writer | **FIX** |
| 3 | [ ] M-08 | Major (platform) | No PreToolUse hook enforces the pinned subagent model at dispatch (Issue #22a) | **ISSUE** (Issue #22) |
| 4 | [ ] M-06 | Major (platform+doc) | Analyzer only parses guard-audit records; conductor gate records corrupt tool-call counts | **ISSUE** (Issue #22) |
| 5 | [ ] M-07 | Major (guarantee) | Analyzer report shows transcript model as "pinned model" with no planned-vs-actual / mismatch flag | **ISSUE** (Issue #22) |
| 6 | [x] M-01 | Major (platform) | Primary command documents itself as bare `/implement-feature`, inconsistent with sibling commands' namespacing | **FIX** |
| 7 | [ ] M-03 | Major (platform+doc) | SKILL.md prose claims reviewers run at `high` effort; all agent-defs pin `medium` | **ISSUE** (needs a real budget/cost decision) |
| 8 | [ ] M-02 | Major → downgraded | `01-requirements.md` missing from IMPLEMENT inbox table/prose (superseded by m-04's narrower framing) | fold into #9 |
| 9 | [x] m-04 | Minor | Same as above, corrected framing: SKILL table/prose (not the agent-def) omits `01-requirements.md` | **FIX** |
| 10 | [x] m-06 | Minor (guarantee) | Reviewer write-confinement allowlist uses unanchored substrings (`scratchpad`, `/handoff/`) — spoofable path escapes confinement | **FIX** |
| 11 | [x] m-05 | Minor (guarantee) | Secrets guardrail misses directory-scoped `grep -r`/`Grep` reads and `Edit` targets | **FIX** |
| 12 | [ ] m-07 | Minor (guarantee/doc) | Guard write-confinement covers `test-reviewer` only; verifier/code-reviewer are nominally read-only but unenforced | **ISSUE** (design-intent decision) |
| 13 | [ ] m-03 | Minor | Same asymmetry as m-07, from the agent-def side (Unit 3) | fold into #12 |
| 14 | [x] m-01 | Minor | VERIFY inbox table omits `<code_root>/` (prose has it correctly) | **FIX** |
| 15 | [ ] m-09 | Minor (guarantee) | Conductor still writes a guessed `model`/`effort` for `[I]` gates (Issue #22c unmet) | **ISSUE** (Issue #22) |
| 16 | [ ] m-08 | Minor (guarantee) | SKILL.md overclaims the model pin "never deviate[s]" | **ISSUE** (Issue #22, reword alongside M-08) |
| 17 | [ ] m-10 | Minor | No test exercises the mixed-schema run-log or a model mismatch flag | **ISSUE** (Issue #22, add tests with M-06/M-07 fix) |
| 18 | [x] m-11 | Minor | Issue #22 references a `design/model-pinning-findings.md` that no longer exists | **FIX** (amend issue text) |
| 19 | [x] m-12 | Minor | Two reference docs call the requirements handoff `requirements.md` instead of `01-requirements.md` | **FIX** |
| 20 | [x] m-16 | Minor | Same wrong filename in `docs/user-guide.md` (user-facing) | **FIX** |
| 21 | [x] m-13 | Minor | CLAUDE.md/developer-guide/tutorial all undercount guard jobs at four (real: five, missing draft-confinement) | **FIX** |
| 22 | [x] m-14 | Minor | Same three docs omit `NotebookEdit` from the guard's matched-tool enumeration | **FIX** |
| 23 | [x] m-15 | Minor | developer-guide.md's handoff table duplicates the M-02/m-04/m-01 omissions verbatim | **FIX** (bundle with #9/#14) |
| 24 | [ ] m-02 | Minor → superseded | Model-plan table blank reviewer effort cells (superseded by M-03) | fold into #7 |
| 25 | [ ] m-17 | Minor | `REFACTOR-PLAN.md`/`RESUME.md` (588 lines) are tracked at repo root, not gitignored | **FIX** (confirm with user: delete vs gitignore) |
| 26 | [x] N-01 | Nit | toy-greet-plugin manifest omits `license` field vs implement-feature-plugin's `MIT` | **FIX** |
| 27 | [x] N-02 | Nit | implementer.md doesn't mention its test-edit denial is guard-enforced (test-reviewer.md does) | **FIX** |
| 28 | [x] N-03 | Nit | guard.py docstring omits `NotebookEdit` from its own tool list | **FIX** |
| 29 | [x] N-04 | Nit | DEVCONTAINER.md typo: "wotkflow" → "workflow" | **FIX** |
| 30 | [x] N-05 | Nit | tutorial.md uses slash-command form for `marketplace add` but CLI form for `install`, inconsistent with its own stated rule | **FIX** |

### Recommended execution order

1. **Batch A — fix now, one small PR, no design decisions needed** (mechanical/doc/small-code, rows
   9, 11, 14, 18–23, 26–30, plus M-01 and m-01): filename/typo/enumeration corrections, the M-01
   command-naming fix, and the secrets-guardrail (m-05) and reviewer-confinement-anchoring (m-06)
   code fixes. These are independently verifiable and low-risk.
2. **Batch B — fix now, security-sensitive but still self-contained** (M-04, M-05): close the two
   Bash-bypass holes in `guard.py` (test-integrity, algorithm-blindness) plus their regression tests.
   These defend the product's two headline "guarantees," so treat as higher urgency than Batch A even
   though the code change is still local to `guard.py`.
3. **Batch C — file GitHub issues, don't fix inline**:
   - One issue for **M-03** (effort medium-vs-high) — it's a real budget/cost tradeoff the user should
     decide, not something to silently pick a side on.
   - One issue for **m-07/m-03** (verifier/code-reviewer write-confinement asymmetry) — same reasoning,
     a deliberate design choice or a scope extension.
   - Roll **M-06, M-07, M-08, m-08, m-09, m-10, m-11** into the existing **Issue #22** (model
     integrity) — they're all facets of the same enforcement/detection gap and were already
     cross-referenced against it during this review; fixing them piecemeal would fragment that issue.
4. **Batch D — a decision, not a fix**: **m-17** (tracked `REFACTOR-PLAN.md`/`RESUME.md`) — confirm
   with the user whether the refactor is complete before deleting or gitignoring.

## Unit status
| # | Unit                              | Status | Session date |
|---|-----------------------------------|--------|--------------|
| 1 | Manifests & wiring                | done   | 2026-09-11   |
| 2 | SKILL.md conductor                | done   | 2026-09-11   |
| 3 | Agent defs                        | done   | 2026-09-11   |
| 4 | Guard hook                        | done   | 2026-09-11   |
| 5 | Analyzer                          | done   | 2026-09-11   |
| 6 | References, templates, toolchain  | done   | 2026-09-11   |
| 7 | Docs, top-level & synthesis       | done   | 2026-09-11   |

## Executive summary

This review covered the whole repo across 7 units, read-only, at line granularity. Bottom line: the
product's **behavior is real and mostly matches the docs**, but the docs **oversell precision they
don't have** in exactly the two places that matter most for a "guarantees" product — test integrity
and algorithm-blindness under `Bash` (M-04, M-05) — and the **model-integrity story (Issue #22)** is
still open on both the prevention side (M-08: no dispatch-time enforcement) and the detection side
(M-06/M-07: the analyzer drops the run-log's declared model and never flags a pin↔transcript
mismatch). Everything else is Frame-1 drift: the same 2-3 small inconsistencies (an omitted
`01-requirements.md` in an inbox table, a missing `<code_root>/`, a wrong `requirements.md` filename,
an undercounted "four guard jobs") **recur near-verbatim across SKILL.md, the developer guide, and the
user guide** — evidence these docs were hand-copied rather than generated from one source, and that a
maintainer fixing one occurrence is likely to miss the siblings.

**Highest-priority opens, by frame:**
- **Frame 3 (guarantee doesn't hold):** M-04 (test-integrity has no Bash defense — an implementer can
  `sed -i`/heredoc a test file undenied), M-05 (algorithm-blindness defeatable by a wildcard `cat
  handoff/*.md`), M-08 (no enforcement that a pinned subagent actually launches on its pinned model).
- **Frame 2 (platform reality):** M-01 (bare `/implement-feature` vs the plugin's own namespacing
  convention, repeated across README/user-guide/tutorial — see M-11 below), M-06 (analyzer mis-parses
  the heterogeneous run-log), M-03 (docs claim reviewers run at "high" effort; every agent-def pins
  `medium`).
- **Frame 1 (internal consistency):** a cluster of inbox-table omissions (M-02/m-01/m-04, corroborated
  again in developer-guide.md by M-11-adjacent findings below) and the guard-denial-count /
  `NotebookEdit` doc-undercounts (m-13, m-14) that recur across CLAUDE.md, developer-guide.md, and
  tutorial.md.

**Structural:** `REFACTOR-PLAN.md` (502 lines) and `RESUME.md` (86 lines) are git-tracked at the repo
root, not gitignored — transient refactor scaffolding shipping alongside the v1 product (m-17).

**Not found:** no evidence of a *false* claim about what the guard enforces once Unit 4 traced the
actual code (the "5 vs 4 denials" scare resolved to real-but-underdocumented); the three-audience
README routing genuinely holds — each guide stays in its lane and cross-links correctly; the toy
example (`toy-greet-plugin/`) matches the tutorial's narrative exactly, including its "~35 lines" claim
and the namespacing rule it's used to illustrate.

## Deferred to later units (working notes, not findings)
- **Tracked scaffolding:** `REFACTOR-PLAN.md` and `RESUME.md` are git-tracked (`git ls-files`
  confirms). Per Scope this is a structural-weakness finding, but REVIEW-PROMPT assigns
  tracked-scaffolding flags to **Unit 7** — record the formal finding there. Caches
  (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`) are present on disk but **not**
  tracked, and are correctly covered by `.gitignore` — no finding.
- **hooks.json matcher vs docs:** `hooks.json:5` matcher is
  `Read|Bash|Grep|Glob|Edit|Write|NotebookEdit`; `CLAUDE.md` enumerates only
  "Read/Bash/Grep/Glob/Edit/Write" (no NotebookEdit). Whether `guard.py` handles NotebookEdit
  is a **Unit 4** question; the doc-enumeration drift is a **Unit 7** doc↔config synthesis item.
  Noted here so it isn't lost.
- **Guard denial SET differs across docs — resolve in Unit 4/7 (potentially Frame 3):**
  `SKILL.md:112-123` lists **five** guard denials: (1) `.env`/keys/creds any agent, (2)
  `03-design-internal.md` for test-writer, (3) **anything under `handoff/draft/` for any
  subagent**, (4) Edit/Write to a test file for implementer, (5) writes outside outbox+scratch
  for test-reviewer. `CLAUDE.md` and REVIEW-PROMPT Frame-3 name only **four** — omitting the
  `handoff/draft/` denial (#3). **Unit 4 must check which set `guard.py` actually enforces:** if
  the code enforces 4 but SKILL claims 5, denial #3 is a *false guarantee* (Frame 3, likely
  Critical). If the code enforces 5, then `CLAUDE.md` is merely incomplete (Unit 7 doc drift).
- **Guard AUDIT tool scope:** `SKILL.md:110` says the audit records "every Read/Bash/Grep/Glob",
  but `hooks.json:5` also matches Edit/Write/NotebookEdit. Unit 4: confirm whether `guard.py`
  audits all matched tools or only read-like ones (and whether the narrower doc claim is wrong).
- **Mixed-schema run-log:** `SKILL.md:104-111` has the conductor append gate records
  (`{gate,mode,agent,model,effort,inbox,outbox,result,ts}`) AND the guard append audit records
  (`{ts,agent_type,agent_id,tool,target}`) to the **same** `handoff/run-log.jsonl`. Unit 5 must
  confirm the analyzer parses both record shapes from one heterogeneous JSONL file.
- **Unit 3 corroborations (bookkeeping):** `implementer.md:15` **includes** `01-requirements.md`
  in the implementer inbox, and `verifier.md:15-18` includes `<code_root>/` — i.e. the two
  agent-defs get the inbox right where SKILL's summary table was wrong (see M-02→m-04, m-01).
- **Verifier/code-reviewer write-confinement — Unit 4 check:** SKILL's guard list (112-123)
  confines writes for **test-reviewer only**, yet `verifier.md` (Read,Bash) and `code-reviewer.md`
  (Read,Grep,Glob,Bash) are also nominally read-only and both hold `Bash` (heredoc-writable).
  Unit 4: confirm whether `guard.py` leaves verifier/code-reviewer writes unconfined (see m-03).
  **RESOLVED in Unit 4 → m-07:** `guard.py:233` confines `test-reviewer` only; verifier &
  code-reviewer writes are unconfined.

### Unit 4 resolutions of prior deferred notes
- **Denial SET 5-vs-4 (was potential Frame-3 Critical): RESOLVED — no false guarantee.**
  `guard.py` enforces **all five** denials SKILL.md claims: secrets (`guard.py:209`),
  algorithm-blind (`:215`), **draft-confinement `handoff/draft/` (`:222`, and a test covers it,
  `test_guard.py:71`)**, test-integrity (`:227`), reviewer-confinement (`:233`). So denial #3
  (draft-confinement) is real; `CLAUDE.md`/REVIEW-PROMPT naming only four omit it → mere
  **doc incompleteness**, to record in Unit 7 (not a Frame-3 gap).
- **Audit tool scope: confirmed broader than SKILL claims.** `guard.py:186` audits
  **unconditionally, before any tool filter**, so every matcher-matched tool
  (Read/Bash/Grep/Glob/Edit/Write/NotebookEdit) is logged, not just "every Read/Bash/Grep/Glob"
  as `SKILL.md:110` states. Understatement → Unit 7 doc drift.
- **hooks.json matcher includes NotebookEdit: confirmed handled.** `WRITEISH` (`guard.py:103`)
  includes `NotebookEdit`, so test-integrity/reviewer-confinement cover it. But the guard's own
  docstring omits it → N-03.

### Unit 5 notes — analyzer deep-dive + Issue #22 verification matrix
The user directed a super-deep dive on the analyzer and on Issue #22
("Model integrity: enforce the launched subagent model + report only the actual model").
This session did Unit 5 (analyzer) in full **and** appended cross-cutting Issue #22 findings
against units already `done` (labeled with their real unit). Verification of each Issue #22
item against the **current branch** (`refactor/shippable-plugin`):

| Issue #22 requirement | Current-branch reality | Finding |
|---|---|---|
| (a) Enforce launched model via PreToolUse deny+respawn hook on `Task`/`Agent` dispatch, integrated into `guard.py` | **Absent.** `hooks.json:5` matcher = `Read\|Bash\|Grep\|Glob\|Edit\|Write\|NotebookEdit` (no `Task`/`Agent`); `guard.py` has no `subagent_type`/`tool_input.model`/frontmatter read and no deny+respawn. | **M-08** (Unit 4) |
| (a-doc) invariant claim | `SKILL.md:214` "**never deviate**" + `:219-220` "regardless of what this environment resolves `opus` to" overstate a rank-2 pin the platform does not guarantee. | **m-08** (Unit 2) |
| (b) Analyzer transcript-derived model = single source of truth | **MET.** `transcript.py:164-176,256-264` sources model only from `message.model`; `report.py` renders only transcript models. | — |
| (b) Add run-log↔transcript **mismatch guard** | **Absent.** Analyzer never reads the run-log's `model` field (it is dropped, see M-06) and never compares; `SKILL.md:125` calls this "cross-checks" — overstated. | **M-07** (Unit 5) |
| (c) No guessed model; **conductor stops writing `model` for `[I]` gates** | **UNMET.** `SKILL.md:105` still writes `{…, model, effort, …}` for every gate incl. `[I]`; the conductor cannot observe a subagent's resolved model, so it is a guess. | **m-09** (Unit 2) |
| (c) Clearly label planned vs. actual model | **UNMET.** `report.py:82-91` shows the transcript-actual model under a single "Model" column that `analyze-run.md:2,14-16` + `SKILL.md:597` call the "**pinned** model" — the exact planned/actual conflation the issue forbids. | **M-07** (Unit 5) |
| Acceptance: unit tests cover enforcement + mismatch check | **UNMET.** No enforcement hook to test; no analyzer test feeds a conductor gate record or asserts a mismatch flag. | **m-10** (Unit 5) |
| Acceptance: `design/model-pinning-findings.md` reflects verified reality | **File does not exist** anywhere in the tree (`git ls-files` empty; likely removed by "delete absorbed/stale docs"). Criterion unsatisfiable as written. | **m-11** (Unit 5) |

**Mixed-schema confirmation (the standing Unit-5 deferred question):** `run-log.jsonl` is
heterogeneous — conductor gate records `{gate,mode,agent,model,effort,inbox,outbox,result,ts}`
(`SKILL.md:103-106`) interleaved with guard audit records `{ts,agent_type,agent_id,tool,target}`
(`guard.py:187-196`), both to the identical path (`guard.py:42` resolves `<workdir>/handoff/run-log.jsonl`
= the conductor's `<artifact_dir>/handoff/run-log.jsonl`). The analyzer parses **only** the guard
shape → **M-06**.

**Analyzer logic pass (no further findings):** the transcript reader is sound — window padding is
symmetric between `find_transcript` and `parse_transcript` (`transcript.py:106,135-136`) so the
drift self-check cannot false-positive from windowing; subagent turns are written to a sibling dir,
not inline, so folding them into `sidechain` (`:192-203`) does not double-count; `parse_ts` tolerates
both `Z` and naive stamps; malformed lines/files are skipped-and-counted throughout. Isolation
verdicts are **not** corrupted by the mixed-schema bug (gate records carry `agent`, not `agent_type`,
so they land in the conductor bucket and never touch the test-writer/implementer/reviewer/`seen`
checks) — which is why M-06 is Major (count/data corruption), not Critical.

## Findings

### M-01
- **Severity:** Major
- **Frame:** 2 (platform reality)
- **Unit:** 1
- **Location:** `implement-feature-plugin/commands/implement-feature.md:5` (title `# /implement-feature — conductor entry point`) and line 1-8 body, which repeatedly call it `/implement-feature`. Contrast: same plugin's `commands/analyze-run.md:6` uses the namespaced `# /implement-feature:analyze-run`, and `toy-greet-plugin/commands/greet.md:6` explicitly notes "Invoked as /toy-greet:greet (plugin commands are namespaced by plugin name)."
- **Claim vs. reality:** The product's primary entry-point command documents itself as bare `/implement-feature`. Claude Code plugin commands are namespaced `/<plugin>:<command>`; with plugin name `implement-feature` and command file `implement-feature.md`, the canonical invocation is `/implement-feature:implement-feature`. The repo's *other two* command files use the namespaced form, so the bare form here is internally inconsistent with the author's own documented convention.
- **Why it matters:** This is the first thing a stranger types. If the bare form does not resolve (or resolves ambiguously), install-to-run breaks at step one — the highest-impact place to be wrong. Even if Claude Code accepts an unambiguous short form, the doc is inconsistent with the two sibling commands and with the toy plugin's stated rule.
- **Recommendation (advisory):** Standardize on `/implement-feature:implement-feature` in the command title/body (or explicitly document that the short form is accepted and why), matching `analyze-run.md` and `greet.md`. Verify the actual resolved command name in a real session before shipping the docs.
- **Status:** fixed — command title changed to `/implement-feature:implement-feature`.

### N-01
- **Severity:** Nit
- **Frame:** 1 (internal consistency)
- **Unit:** 1
- **Location:** `toy-greet-plugin/.claude-plugin/plugin.json:1-10` (no `license` field) vs `implement-feature-plugin/.claude-plugin/plugin.json:6` (`"license": "MIT"`).
- **Claim vs. reality:** The two sibling plugins in the same marketplace declare metadata inconsistently — one pins a license, the other omits it.
- **Why it matters:** Cosmetic/metadata drift only; both are still valid manifests. A published marketplace reads more polished when sibling manifests carry the same fields.
- **Recommendation (advisory):** Add `"license": "MIT"` (or the intended license) to the toy plugin manifest, or drop it from both if intentionally unlicensed.
- **Status:** fixed — added `"license": "MIT"` to toy-greet-plugin's manifest.

### M-02
- **Severity:** Major
- **Frame:** 1 (internal consistency)
- **Unit:** 2
- **Location:** `implement-feature-plugin/skills/implement-feature/SKILL.md` — inbox table row `| IMPLEMENT [I] | tests + full design |` (line 76) and Gate 5 prose "Its inbox is the **tests** + the **full** design (`02-design-interface.md` + `03-design-internal.md`) + the standards file." (line 445), vs Gate 5 step 1 "honor the constraints in **01-requirements.md**." (line 448).
- **Claim vs. reality:** The IMPLEMENT gate is explicitly told to honor the constraints recorded in `01-requirements.md`, but `01-requirements.md` is in **neither** the summary inbox table row **nor** the Gate 5 prose inbox. The design files (02/03) and test plan (04) do not carry the requirements' **Constraints bucket** ("mandated/forbidden tech, libraries, patterns, style" — Gate 1, lines 317-318); those live only in `01-requirements.md`.
- **Why it matters:** If the conductor briefs the implementer with the inbox as written, the implementer never receives the constraints artifact and can silently use a forbidden library or violate a mandated pattern. It is only caught later at CODE-REVIEW (line 499 checks "the constraints in `01-requirements.md` honored"), costing an extra IMPLEMENT→VERIFY→REVIEW loop for something the handoff should have prevented. A gate's declared inbox must carry every artifact its task references.
- **Recommendation (advisory):** Add `01-requirements.md` to the IMPLEMENT inbox in both the table (line 76) and the Gate 5 prose (line 445), consistent with VERIFY and CODE-REVIEW which both list `01-requirements.md`.
- **Status:** downgraded-by:m-04

### m-01
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 2
- **Location:** `SKILL.md` inbox table row `| VERIFY [I] | `01-requirements.md` (ACs + boundary inventory) |` (line 77) vs Gate 6 prose "Its inbox: `01-requirements.md` (the ACs + boundary inventory) and `<code_root>/` (to invoke the real thing...)" (line 468).
- **Claim vs. reality:** The summary inbox table lists only `01-requirements.md` for VERIFY, omitting `<code_root>/`. The verifier's entire job is to "invoke the **real** public function/flow" (line 471), which is impossible without read access to `<code_root>/`; the prose correctly includes it.
- **Why it matters:** Low impact (the Gate 6 prose corrects it and is what a reader ultimately follows), but the summary handoff table — the at-a-glance contract — understates what VERIFY needs.
- **Recommendation (advisory):** Add `<code_root>/` to the VERIFY inbox cell in the table (line 77).
- **Status:** fixed — `<code_root>/` added to the VERIFY inbox table cell (SKILL.md).

### m-02
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 2
- **Location:** `SKILL.md` model-plan table, "Model / effort" column: `| TEST-REVIEW | [I] `test-reviewer` | **`claude-opus-4-8`** (pinned) | ...` (line 208) and `| CODE-REVIEW | [I] `code-reviewer` | **`claude-opus-4-8`** (pinned) | ...` (line 211) — both give a model but **no effort** — vs Gate 4 prose "Opus/**high** per the model plan" (line 411) and Gate 7 prose "Opus/**high**" (line 490).
- **Claim vs. reality:** The column header is "Model / effort", and every other row states an effort (e.g. "Opus (session), medium"; "sonnet alias, medium"), but the two reviewer rows omit the effort while the gate prose and the invariant ("higher model **or effort**") depend on the reviewers running at `high`.
- **Why it matters:** Internal drift; a reader consulting the canonical model-plan table can't see the reviewers' `high` effort that the prose and (per Unit 3) the agent-defs pin. The effort half of the "higher model/effort than implementation" invariant is invisible for exactly the two review rows it most matters for.
- **Recommendation (advisory):** Write "`claude-opus-4-8` (pinned), high" in both reviewer rows to match the prose and the agent-def frontmatter.
- **Status:** superseded-by:M-03 _(this finding's premise — that the reviewers run at `high` — is wrong; Unit 3 found the agent-defs pin `effort: medium`, so the table's blank effort should read `medium`, not `high`. M-03 states the corrected, broader issue.)_

### M-03
- **Severity:** Major
- **Frame:** 2 (platform reality) — with Frame-1 doc drift
- **Unit:** 3
- **Location:** All five agent-defs pin `effort: medium` (`test-writer.md:5`, `test-reviewer.md:5`, `implementer.md:5`, `verifier.md:5`, `code-reviewer.md:5`). SKILL.md's per-gate prose contradicts this in four gates: Gate 4 "(Opus/**high** per the model plan; pinned in `agents/test-reviewer.md`)" (line 411); Gate 5 "(Sonnet/**high**; ... pinned in `agents/implementer.md`)" (line 443); Gate 6 "(Sonnet/**high**; ... pinned in `agents/verifier.md`)" (line 466); Gate 7 "(Opus/**high**; pinned in `agents/code-reviewer.md`)" (line 490).
- **Claim vs. reality:** SKILL.md repeatedly states the subagents run at `high` effort — and each time cites the very agent-def as the source — but every agent-def actually pins `medium`. Per the platform (and this repo's own CLAUDE.md / Frame-2 rule), `effort` is settable **only** via agent-def frontmatter, not inline; the frontmatter therefore wins, so every subagent runs at **medium**, and all four "/high" claims are false.
- **Why it matters:** (1) Frame-2: the runtime effort is medium, not the high the docs promise, so the reviewers and implementer run with less reasoning budget than the score advertises — a real behavior/expectation gap. (2) The "design & every review use a higher model **or effort** than implementation" invariant is satisfied here **only via model** (opus>sonnet for reviewers), never via effort — impl and reviewers share `medium`. The prose's "/high" masks that the effort axis contributes nothing, and worse, claims impl/verify run at "high" too (they don't). (3) A maintainer reading "pinned in agents/X.md ... high" and opening that file finds `medium` — direct self-contradiction with the cited source.
- **Recommendation (advisory):** Reconcile to one value. Either (a) change all four SKILL prose sites to `medium` to match the defs (and fill the model-plan table's two blank reviewer-effort cells with `medium`), or (b) if `high` for the reviewers is actually intended, change `test-reviewer.md`/`code-reviewer.md` frontmatter to `effort: high` and fix the prose for implementer/verifier (which should stay `medium`). Decide deliberately, since it changes real reasoning budget.
- **Status:** open

### m-03
- **Severity:** Minor
- **Frame:** 1 (internal consistency) — Unit 4 to confirm against `guard.py`
- **Unit:** 3
- **Location:** `verifier.md:6-7` (`tools: Read, Bash` / `disallowedTools: Write, Edit`) and `code-reviewer.md:6-7` (`tools: Read, Grep, Glob, Bash` / `disallowedTools: Write, Edit`), vs SKILL.md's guard-enforcement list which confines writes for the **test-reviewer only** (lines 121-122), and vs `test-reviewer.md:42-46` which explicitly warns that `disallowedTools` is "documentation-only" because a `Bash` heredoc can still write and "the guard hook enforces the real rule."
- **Claim vs. reality:** By the test-reviewer def's own logic, `disallowedTools: Write, Edit` does not actually make a Bash-holding agent read-only — only the guard does. The verifier and code-reviewer are equally Bash-holding and equally declared read-only, yet the docs design guard write-confinement for the test-reviewer alone. As written, verifier/code-reviewer read-only-ness rests on prose + a `disallowedTools` field the repo itself calls non-binding.
- **Why it matters:** A verifier or code-reviewer could, via a Bash heredoc, mutate the product tree (`<code_root>`/`<tests_root>`) and the guard would audit but not deny it. The bias risk is lower than the test-reviewer's (the implementation already exists, so there's no "build a reference impl before tests" concern), so this is likely a defensible design choice rather than a hole — but the asymmetry is undocumented and worth an explicit rationale.
- **Recommendation (advisory):** Either extend guard write-confinement to verifier/code-reviewer (scratch-dir-only, same as test-reviewer), or add one sentence to their defs / SKILL explaining why they are intentionally *not* confined. Unit 4 will confirm what `guard.py` actually does.
- **Status:** open

### m-04
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 3
- **Location:** `implementer.md:15` lists `01-requirements.md` in the implementer inbox, and SKILL.md Gate 5 step 1 (line 448) instructs it to "honor the constraints in `01-requirements.md`" — but SKILL.md's summary inbox table (line 76) and Gate 5 prose inbox (line 445) both omit `01-requirements.md`.
- **Claim vs. reality:** This finding **downgrades M-02**. M-02 asserted the implementer "never receives the constraints artifact." Unit 3 shows the agent-def — which the spawned agent actually follows — *does* include `01-requirements.md` in its inbox, so the constraints are reachable in practice. The defect is narrower than M-02 stated: SKILL.md's own summary table (76) and prose inbox (445) are internally inconsistent with both `implementer.md:15` and SKILL.md's own Gate-5 step-1 instruction. It is doc-consistency drift, not a functional guarantee gap.
- **Why it matters:** Low functional risk (the agent-def carries `01`), but the SKILL handoff contract — the at-a-glance source of truth — misstates the implementer's inbox, and a maintainer trusting the table over the def could "fix" the def by removing `01`, reintroducing the real gap.
- **Recommendation (advisory):** Same as M-02 — add `01-requirements.md` to SKILL.md's IMPLEMENT inbox (table line 76 + prose line 445) so all three sources agree.
- **Status:** fixed — `01-requirements.md` added to SKILL.md's IMPLEMENT inbox (table + Gate 5 prose) and to developer-guide.md's handoff table (m-15).

### N-02
- **Severity:** Nit
- **Frame:** 1 (internal consistency)
- **Unit:** 3
- **Location:** `implementer.md:28` ("Do not weaken or edit tests to pass.") — prose only, with no mention of the guard-hook enforcement — vs `test-reviewer.md:42-46`, which fully documents that its own read-only-ness is guard-enforced (and why `disallowedTools` alone is insufficient).
- **Claim vs. reality:** Test-integrity (implementer must not edit tests) is a headline isolation guarantee (SKILL 456-458, invariant "c"), enforced by the guard. The implementer def documents only the soft prose rule and never notes that the guard will *deny* a test edit, while the structurally similar test-reviewer def explains its guard enforcement in full. Documentation depth is asymmetric for the more safety-critical of the two.
- **Why it matters:** Cosmetic/defense-in-depth-documentation only; enforcement lives in `guard.py` regardless. But a reader of `implementer.md` alone would not learn that the rule is hard-enforced.
- **Recommendation (advisory):** Add a one-line note to `implementer.md` mirroring the test-reviewer's: edits/writes to any test file are denied by the guard hook (keyed on `agent_type`), not just discouraged.
- **Status:** fixed — added a note to implementer.md that the test-edit denial is guard-enforced, mirroring test-reviewer.md.

### M-04
- **Severity:** Major
- **Frame:** 3 (claimed guarantee) — arguably Critical (a headline isolation guarantee is only partially enforced)
- **Unit:** 4
- **Location:** `guard.py:227` (`if "implementer" in agent_type and tool in WRITEISH and is_test_path(target)`) with `WRITEISH = {"Write", "Edit", "NotebookEdit"}` (`guard.py:103`), vs `implementer.md:6` (`tools: Read, Write, Edit, Bash` — the implementer **holds Bash**). Test coverage: `test_guard.py:119-125` exercises only `Write`.
- **Claim vs. reality:** The docs sell test-integrity as a hard guard-enforced guarantee: SKILL invariant "(c)" and `guard.py:11-12` ("deny the implementer editing/writing **any** test file"). But the clause fires **only for `Write`/`Edit`/`NotebookEdit`** — `Bash` is not in `WRITEISH` and has no separate test-file check. The implementer holds `Bash`, so `sed -i 's/assert x/pass/' tests/test_foo.py`, `cat > tests/test_foo.py <<'EOF' … EOF`, or `python -c "open('tests/test_foo.py','w').write(...)"` **weaken/overwrite tests undenied** (audited only). This is exactly the P44 Bash-bypass class the reviewer-confinement (`guard.py:238-243`, `bash_write_targets`) was purpose-built to defend — yet test-integrity, the *more* safety-critical guard, has no Bash defense at all. (Secondary gap: `is_test_path` (`guard.py:105-109`) requires `/tests/` **with slashes** or a `test_`/`_test.py`/`conftest.py` basename, so a relative `tests/helpers.py`-style non-`test_` file inside a tests dir isn't matched either.)
- **Why it matters:** The single guarantee that makes "green tests" trustworthy — the implementer cannot cheat by editing the tests — is bypassable with one Bash call by the very agent it targets, which routinely uses Bash to run the suite. A tuned-to-pass run would look green and pass CODE-REVIEW's mutation check on tests the implementer quietly loosened. The test suite gives false confidence: it asserts only the `Write` path, so the hole is invisible to the tests.
- **Recommendation (advisory):** Extend the implementer clause to `Bash` using the existing `bash_write_targets(target)` machinery (deny if any resolved write/redirect target `is_test_path`), and consider `sed -i`/`tee`/`cp`/`mv`/`python -c open()` forms. Add a regression test for `cat > tests/test_*.py <<EOF` and `sed -i … tests/…` under the implementer agent_type.
- **Status:** open

### M-05
- **Severity:** Major
- **Frame:** 3 (claimed guarantee)
- **Unit:** 4
- **Location:** `guard.py:215` (`if "test-writer" in agent_type and "design-internal" in target`) vs `test-writer.md:6` (`tools: Read, Write, Bash` — the test-writer **holds Bash**). Test coverage: `test_guard.py:109-116` exercises only a direct `Read` of the literal filename.
- **Claim vs. reality:** Algorithm-blindness (SKILL invariant "(b)"; `guard.py:7` "deny reads of design-internal for the test-writer") is enforced by a **literal substring** match on `"design-internal"` in the tool target. For `Read`/`Bash` of the exact path (`…/03-design-internal.md`) that trips (the Bash target is the whole command string, which contains the substring). But the test-writer holds `Bash`, so a **wildcard** read — `cat handoff/*.md`, `cat handoff/03*.md`, `head handoff/0[23]-*` — reads the internal design's contents while the command string never contains the literal `"design-internal"`, so it is **not denied**. Draft-confinement (`:222`) does not help: the internal design is a *promoted* file at `handoff/03-design-internal.md`, not under `handoff/draft/`. The algorithm-blind property therefore rests on the agent spelling the forbidden filename in full.
- **Why it matters:** The interface/internal design split is the product's central bias control — the test-writer must never see the algorithm. One glob (`cat handoff/*.md`, a natural way to "read my whole inbox") leaks the internal design and quietly voids the guarantee that the tests are algorithm-blind. As with M-04, the test suite only covers the literal-filename Read, so the bypass is untested.
- **Recommendation (advisory):** Don't rely on filename substring. Deny the test-writer any `Read`/`Bash`/`Glob` whose *resolved* target set could include the internal-design file — e.g. confine the test-writer to an explicit inbox allowlist, or (defense-in-depth) resolve Bash read targets and glob patterns and deny any that could match `*design-internal*`. Add a `cat handoff/*.md` regression test under the test-writer agent_type.
- **Status:** open

### m-05
- **Severity:** Minor
- **Frame:** 3 (claimed guarantee)
- **Unit:** 4
- **Location:** `guard.py:209` (`if tool in READISH and looks_secret(tool, target)`) and target resolution `guard.py:182-183` (`ti.get("file_path") or ti.get("path") or … or ti.get("pattern")`).
- **Claim vs. reality:** The secrets guardrail is sold as "deny reads of .env / keys / credentials for **ANY** agent" (`guard.py:6`). It is **path-target based**: for non-Bash tools it matches `_is_secret_path(target)`, and for Bash it scans path-like tokens. Two gaps: (1) a **directory-scoped read** surfaces secret *contents* without the target being a secret path — `grep -r AWS_SECRET /repo` (Bash: tokens are `grep`,`-r`,`AWS_SECRET`,`/repo`, none secret) or a `Grep pattern=… path="/repo"` (target resolves to the directory `/repo`) returns matching lines from `/repo/.env` un-denied. (2) The guardrail only fires for `READISH` (`Read/Bash/Grep/Glob`); an `Edit` targeting `.env` (which reads the file to diff) is not covered.
- **Why it matters:** Lower impact than M-04/M-05 (it needs a broad grep rather than a direct open, and a cooperating agent has no reason to), but the guarantee is stated absolutely ("ANY agent"), and a recursive grep over the repo is a common, innocent-looking action that would exfiltrate `.env` contents into a gate's context.
- **Recommendation (advisory):** Treat directory/recursive reads conservatively (e.g. deny `grep -r`/`Grep` over a tree that contains a secret file, or strip secret files from results), and include `Edit` in the secret check.
- **Status:** fixed — secrets guardrail now also fires on `Edit`, and denies a directory-scoped `Grep`/recursive-Bash-search (`grep -r`, `rg`, `ag`, `find`) over a directory containing a secret file. Regression tests added.

### m-06
- **Severity:** Minor
- **Frame:** 3 (claimed guarantee)
- **Unit:** 4
- **Location:** `guard.py:116-131` — `_is_scratch_path` (`"scratchpad" in t`, `"/scratch/" in t`, `"/tmp"` prefix) and `reviewer_write_denied` (`if "/handoff/" in t or t.startswith("handoff/"): return False`).
- **Claim vs. reality:** Reviewer write-confinement's allowlist uses **unanchored substring** checks. Any product-tree path that merely *contains* `scratchpad`, `/scratch/`, or `/handoff/` is treated as sanctioned and the write is allowed. So a test-reviewer writing `/repo/src/scratch/ref.py` (`"/scratch/"` matches), `/repo/scratchpad_util.py` (`"scratchpad"` matches), or `/repo/src/handoff/impl.py` (`"/handoff/"` matches) **escapes confinement** and mutates the product tree — the very thing the guard exists to prevent ("build no reference implementation").
- **Why it matters:** The confinement guarantee is defeatable by path naming. It requires the reviewer to choose such a path, so impact is bounded, but the allowlist should key on the *actual* artifact dir / a real temp root, not any occurrence of the token anywhere in the path.
- **Recommendation (advisory):** Anchor the allowlist: match the run's real `<artifact_dir>/handoff/` (resolved absolute prefix) and a real temp root (`/tmp/`, `/private/tmp/`, `/var/folders/` as path prefixes; `scratchpad`/`scratch` only as a leading path segment under a temp root), not as free substrings.
- **Status:** fixed — scratch-path check anchored to real temp roots (`/tmp/`, `/private/tmp/`, `/var/folders/`); handoff-path check anchored to the run's actual handoff dir (derived from `run-log.jsonl`'s location) instead of a free `/handoff/` substring. Regression tests added for both spoofed-path bypasses.

### m-07
- **Severity:** Minor
- **Frame:** 1 (internal consistency) / 3 (a stated read-only role not hard-enforced)
- **Unit:** 4
- **Location:** `guard.py:233` (`if "test-reviewer" in agent_type:` — the **only** agent whose writes are confined) vs `verifier.md:6` (`tools: Read, Bash`; `disallowedTools: Write, Edit`) and `code-reviewer.md:6` (`tools: Read, Grep, Glob, Bash`; `disallowedTools: Write, Edit`).
- **Claim vs. reality:** Confirms the m-03 Unit-4 check. `guard.py` write-confinement is scoped to `test-reviewer` alone. The verifier and code-reviewer are declared read-only but both hold `Bash`; by the repo's own reasoning (`test-reviewer.md:42-46`) `disallowedTools` is documentation-only for a Bash-holding agent. So verifier/code-reviewer can mutate the product tree via a Bash heredoc/`sed`/`cp` and the guard **audits but does not deny** it.
- **Why it matters:** Lower bias risk than the test-reviewer's (the implementation already exists, so there is no "reference implementation before tests" concern) — likely a defensible choice — but it is an **undocumented asymmetry**: three agents are declared read-only, only one is hard-enforced.
- **Recommendation (advisory):** Either extend `reviewer_write_denied`-style confinement to verifier/code-reviewer, or add one sentence to their defs / SKILL stating they are intentionally *not* hard-confined and why.
- **Status:** open

### N-03
- **Severity:** Nit
- **Frame:** 1 (internal consistency)
- **Unit:** 4
- **Location:** `guard.py:4` docstring ("Does six jobs on every Read/Bash/Grep/Glob/**Edit/Write**") vs `guard.py:103` (`WRITEISH = {"Write", "Edit", "NotebookEdit"}`) and `hooks.json:5` (matcher includes `NotebookEdit`).
- **Claim vs. reality:** The guard's own docstring omits `NotebookEdit` from the tools it acts on, though the matcher registers it and `WRITEISH` (test-integrity + reviewer-confinement) actually covers it. Cosmetic self-doc drift inside the code.
- **Why it matters:** None functionally; a maintainer reading the docstring underestimates coverage. (Same NotebookEdit omission appears in `CLAUDE.md` / SKILL enumerations — a Unit-7 doc item.)
- **Recommendation (advisory):** Add `NotebookEdit` to the guard docstring's tool list.
- **Status:** fixed — added `NotebookEdit` to guard.py's own docstring tool list.

### M-06
- **Severity:** Major
- **Frame:** 2 (platform reality) — with Frame-1 doc drift
- **Unit:** 5
- **Location:** `analyzer/runlog.py:210-264` (`parse_runlog`), esp. `:236-249` (`atype=rec.get("agent_type")`, `tool=rec.get("tool")`, `target=rec.get("target")`), and docstring `:1-13` ("Parses the guard hook's audit log … one line per tool call"). The written data it fails to handle: `SKILL.md:103-106` (conductor appends `{gate, mode, agent, model, effort, inbox, outbox, result, ts}` to `<artifact_dir>/handoff/run-log.jsonl`) vs `guard.py:187-196` (guard appends `{ts, agent_type, agent_id, tool, target}` to the same path, `guard.py:42`). Render impact: `report.py:30` (`Tool calls: **{total_entries}**`) and `report.py:40-46` (`", ".join(f"{k}×{v}" …)`).
- **Claim vs. reality:** `run-log.jsonl` is **heterogeneous** — the conductor's per-gate orchestration records and the guard's per-tool-call audit records are interleaved in one file, and `--workdir` (the documented primary handle, `analyze-run.md:28-31`) points the analyzer straight at it. `parse_runlog` understands **only** the guard schema. A conductor gate record has no `agent_type`/`tool`/`target`, so each one is counted as a conductor "tool call" with an **empty tool name**: `total_entries` is inflated, `tool_counts[""]` is incremented (rendering a garbage `×N` cell first in the conductor's Tools column, since `sorted` puts `""` first), and the record's real payload — `gate`/`mode`/`agent`/`model`/`effort`/`result` — is **silently dropped**. The module docstring still describes the file as the single-schema guard audit log ("one line per tool call"), so a reader is never told it is mixed.
- **Why it matters:** This corrupts the section the analyzer sells as authoritative — `report.py:24` titles it "Run-log analysis (**stable / load-bearing**)". The headline "Tool calls" count and the conductor's per-tool breakdown are wrong by exactly the number of gates in the run, and every conductor-recorded fact (which model/effort each gate *claimed*, gate results) is thrown away — including the `model` field that Issue #22's mismatch guard (see M-07) would need. This is the precise "does the analyzer parse both record shapes from one heterogeneous JSONL?" question deferred to Unit 5 — answered: **no.** (Isolation verdicts are unaffected — see Unit 5 notes — which is why this is Major, not Critical.)
- **Recommendation (advisory):** Discriminate record shape on read (e.g. presence of `tool`/`agent_type` = audit vs. `gate` = orchestration) and route each to its own aggregation; exclude gate records from tool-call counts and the per-tool column; surface the gate records' `gate`/`result`/declared-model as their own report section (feeding M-07's mismatch check). Fix the `runlog.py` docstring to state the file is mixed-schema. Add a `parse_runlog` test that includes a `{gate,…,model,…}` line and asserts it is not counted as a tool call.
- **Status:** open

### M-07
- **Severity:** Major
- **Frame:** 3 (claimed guarantee)
- **Unit:** 5
- **Location:** `analyzer/report.py:78-93` (`_render_subagent_table`: header "the per-gate model split", single "Model" column sourced from `mu.model` = transcript) and `analyzer/transcript.py` (no run-log comparison anywhere). Docs that name the shown value: `commands/analyze-run.md:2` ("per-gate **pinned** model") and `:14-16` ("each isolated gate's **pinned model** … the evidence for the 'reviews run on a higher model than implementation' invariant"); `SKILL.md:597` ("each isolated gate's **pinned** model"); `SKILL.md:125` ("the deterministic analyzer … **cross-checks** the session transcript for per-agent model"). Issue #22 acceptance: "run-log/transcript mismatch is detected and surfaced" and "clearly label planned vs. actual models."
- **Claim vs. reality:** Issue #22 requires the analyzer to (i) treat the transcript as the single source of truth [MET], (ii) **flag** any run-log↔transcript model disagreement, and (iii) **label planned vs. actual** distinctly. (ii) is entirely absent — the analyzer never reads the run-log's declared `model` (it is dropped, M-06) and never compares, yet `SKILL.md:125` calls the analyzer's behavior a "cross-check." (iii) is inverted: the report shows the transcript-**actual** model but the command/skill docs call that column the "**pinned** model" — the exact planned/actual conflation Issue #22 exists to remove. There is no "pinned (from agent-def)" column beside an "actual (from transcript)" column and no drift flag.
- **Why it matters:** The product's central quality premise is the model invariant (review-tier > impl-tier). The report is sold as its *evidence*, and Issue #22 was filed precisely because a real Phase-4 run recorded `opus-5` while the transcript showed `opus-4-8`. Today the report happens to show the true (transcript) model, so in the happy path it is accurate — but if the rank-2 pin ever silently drops (M-08's scenario), a reviewer running on the wrong model would be surfaced under a column labeled "pinned model" with **nothing** flagging the drift, and the run would read as invariant-compliant when it is not. A guarantee's *evidence* must distinguish planned from observed and alarm on disagreement; this one does neither.
- **Recommendation (advisory):** Read each `[I]` gate's declared model from the run-log's gate records (enabled by the M-06 fix), render a two-column "pinned (planned) vs. actual (transcript)" view, and emit a loud finding when they disagree — mirroring the fail-loud discipline the transcript satellite already uses. Reword `analyze-run.md`/`SKILL.md` from "pinned model" to "actual model (from transcript) vs. pinned." Add a mismatch-flag unit test.
- **Status:** open

### M-08
- **Severity:** Major
- **Frame:** 2 (platform reality)
- **Unit:** 4 (appended cross-cutting per user direction; Issue #22 (a))
- **Location:** `implement-feature-plugin/hooks/hooks.json:5` (`"matcher": "Read|Bash|Grep|Glob|Edit|Write|NotebookEdit"` — no `Task`/`Agent`) and all of `hooks/scripts/guard.py` (no `subagent_type`/`tool_input.model`/agent-def-frontmatter read; no deny+respawn on dispatch). Contrast the invariant sold in `CLAUDE.md` ("agent-definition files pin per-gate models"; "design & every review use a higher model/effort than implementation") and `SKILL.md:199-223`. Issue #22 (a) recommends exactly a PreToolUse deny+respawn hook on `Task`/`Agent` "integrated into `guard.py`," with acceptance "Subagent with pinned model cannot launch on different model — hook forces pinned model at rank-1."
- **Claim vs. reality:** The model invariant rests entirely on the agent-def `model:` frontmatter, which per Issue #22 (and `code.claude.com/docs/en/model-config`) is only **rank 2** in model resolution — an explicit `--model`, an env default, or a resolution-order change across releases can win. Issue #22's recommended enforcement (a `Task`/`Agent` PreToolUse hook that denies a pinned-but-unspecified dispatch so Claude Code re-dispatches with the model at rank 1) **does not exist**: the guard's matcher never fires on subagent dispatch, and the guard has no dispatch-model logic. So nothing *prevents* a pinned subagent from launching on the wrong model — and, combined with M-07, nothing *detects* it afterward either.
- **Why it matters:** The entire "reviews run on a stronger model than implementation" guarantee is unenforced and (post-hoc) unverified: prevention is absent here, detection is absent in the analyzer. A silent pin-drop across a Claude Code release would degrade every review gate to impl-tier with no signal anywhere. Issue #22 marks this "Deferred to later session per owner," so it is a known gap rather than a shipped false claim — but for a v1-labeled, isolation-and-model-integrity-selling product it is a material platform-reality hole, worsened by M-07's missing detection. (See also m-08: the docs meanwhile assert the pin "never deviate[s]".)
- **Recommendation (advisory):** Implement the Issue #22 (a) hook: register a `PreToolUse` matcher for `Task`/`Agent` (a `Task`-matcher entry in `hooks.json`, or a second matcher), have `guard.py` read `tool_input.subagent_type` + `tool_input.model`, resolve the plugin-namespaced agent-def's `model:`, and `exit 2` with a re-dispatch message when pinned-but-unspecified; **fail open** on unparseable payloads; add the four dispatch unit tests the issue lists (pinned+no-model→deny; explicit→allow; unpinned→allow; unparseable→fail-open). Note `effort` cannot be forced this way (agent-def frontmatter only), so the effort half of the invariant remains pin-only (see M-03).
- **Status:** open

### m-08
- **Severity:** Minor
- **Frame:** 3 (claimed guarantee)
- **Unit:** 2 (appended cross-cutting; Issue #22 (a), doc side)
- **Location:** `SKILL.md:214` ("The `[I]` subagent models are pinned in `agents/*.md` and **never deviate**") and `:219-220` ("So the reviewers are `claude-opus-4-8` **regardless of what this environment resolves `opus` to**").
- **Claim vs. reality:** These assert an absolute guarantee the platform does not provide. The `model:` pin is rank-2 in resolution order (M-08); a rank-1 `--model` flag, an env default, or a resolution-order change can override it, and Issue #22 explicitly states the pin "could silently drop across releases" with "no mechanism guaranteeing." "Never deviate" / "regardless of environment" is therefore over-confident. (It is not demonstrably *false today* — Issue #22's own deferred checks found `claude-opus-4-8` was honored — which is why this is Minor, not Major; but the wording claims more than is enforced, and M-08 is the missing enforcement that would make it true.)
- **Why it matters:** The strongest statement of the model invariant in the score tells a maintainer the pin is inviolable, discouraging the very enforcement (M-08) and detection (M-07) that would make it so. Adversarially: a reader who trusts "never deviate" will not add the safeguards Issue #22 asks for.
- **Recommendation (advisory):** Soften to the accurate claim — e.g. "pinned via agent-def frontmatter (model-resolution rank 2); enforced at dispatch by the guard hook" once M-08 lands, or "…and are expected to hold; the analyzer surfaces the actual model per gate as verification" until then. Cross-reference the enforcement/detection story.
- **Status:** open

### m-09
- **Severity:** Minor
- **Frame:** 3 (claimed guarantee) — Issue #22 (c)
- **Unit:** 2 (appended cross-cutting)
- **Location:** `SKILL.md:103-106` — the conductor appends `{gate, mode, agent, **model**, **effort**, inbox, outbox, result, ts}` for **each gate as it completes**, with no carve-out for `[I]` gates. Issue #22 acceptance: "No conductor-written/guessed `model` appears in `run-log.jsonl` for `[I]` gates" and "Conductor stops writing `model` field for `[I]` gates."
- **Claim vs. reality:** Issue #22's fix for defect (1) is that the conductor must stop writing a `model` for isolated gates, because it cannot observe a subagent's *resolved* model (that lives in the subagent transcript) — anything it writes is a guess, which is exactly what produced the `opus-5`-vs-`opus-4-8` discrepancy in the Phase-4 run. The current SKILL still instructs writing `model`/`effort` for every gate record, including the five `[I]` gates. The acceptance criterion is **unmet at the source**. (Its downstream *harm* is now blunted because the analyzer drops the field entirely — M-06 — so the guess no longer reaches the report; but the run-log still contains guessed `[I]` model data, and the criterion is about the run-log, not just the report.)
- **Why it matters:** The run-log is described as a "tamper-evident record" and the orchestration ground truth; seeding it with un-observable guessed model values for the isolated gates undermines that and re-creates the confusion Issue #22 was filed to end. It also means the future mismatch guard (M-07) would be comparing a *guess* against the transcript rather than a genuinely-declared pin — the check must compare the **agent-def pin** to the transcript, not the conductor's guess.
- **Recommendation (advisory):** Drop `model` (and, for `[I]` gates, `effort`) from the conductor-written gate record; if a "planned model" is wanted in the log, source it from the agent-def frontmatter and label it `planned_model`, never a bare `model`. Reconcile with the M-07 mismatch design (compare agent-def pin ↔ transcript).
- **Status:** open

### m-10
- **Severity:** Minor
- **Frame:** 1 (internal consistency) — test adequacy
- **Unit:** 5
- **Location:** `analyzer/tests/test_runlog.py` (every record is built via `conftest.call()` → the guard-audit shape only; no `{gate,…,model,…}` record is ever parsed) and `analyzer/tests/test_report_e2e.py` (same). No test anywhere asserts a run-log↔transcript model mismatch is flagged (there is no such flag — M-07).
- **Claim vs. reality:** The Unit-5 mandate is whether the tests "pin the real behavior." They pin the guard-audit half thoroughly (heredocs, fd-dup, secrets, reviewer confinement) but never exercise the *mixed-schema* reality the run-log actually has (M-06), and cannot exercise a mismatch guard that does not exist (M-07). So both model-integrity gaps are invisible to a green suite.
- **Why it matters:** A passing `python -m pytest analyzer/tests -q` gives false confidence that the analyzer handles a real run-log and satisfies Issue #22's reporting requirements, when it silently mis-parses conductor records and performs no mismatch check.
- **Recommendation (advisory):** Add (a) a `parse_runlog` test feeding a conductor gate record and asserting it is not counted as a tool call / not attributed an empty tool; (b) once M-07 lands, a test asserting a pin↔transcript disagreement is surfaced as a finding. Add a `conftest` factory for gate records so tests can build the mixed file the product actually writes.
- **Status:** open

### m-11
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 5 (Issue #22 acceptance; cross-checked repo-wide)
- **Location:** Issue #22 References + acceptance ("`design/model-pinning-findings.md` reflects verified reality"; "Related repo items: `design/model-pinning-findings.md`"). Repo reality: no `design/` directory exists and `git ls-files | grep -i model-pinning` returns nothing (likely removed by commit "Phase 3: delete absorbed/stale docs").
- **Claim vs. reality:** An open, `v1`-labeled issue's acceptance criteria and references point at a design doc that no longer exists anywhere in the tree, so that criterion is unsatisfiable as written and the reference is dangling.
- **Why it matters:** Low direct product impact (it is issue/tracker hygiene, not shipped behavior), but it means the model-integrity work item can never be "closed to its own acceptance criteria," and anyone following the issue's references hits a missing file. Flagged because the user asked to verify each Issue #22 item against the current branch; also a candidate Unit-7 tracked-scaffolding/stale-reference synthesis item.
- **Recommendation (advisory):** Either restore/relocate the findings doc (e.g. fold verified reality into `docs/developer-guide.md` and update the issue to point there), or amend Issue #22 to drop the dead reference. Decide alongside M-07/M-08 since that is where the "verified reality" would be re-established.
- **Status:** fixed — Issue #22 amended to drop the dangling `design/model-pinning-findings.md` reference; acceptance criterion now points at this issue + `docs/developer-guide.md`.

### m-12
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 6
- **Location:** `implement-feature-plugin/skills/implement-feature/references/quality-standards.md:82` ("honor the constraints in `requirements.md`.") and `implement-feature-plugin/skills/implement-feature/references/design-interface-template.md:28` ("Which acceptance criteria (from `requirements.md`) this surface satisfies.").
- **Claim vs. reality:** Both reference the requirements handoff file as `requirements.md`. The canonical filename used everywhere else in the repo — the SKILL.md handoff table (line 58), every gate's inbox prose (lines 74-78, 335, 381, 413, 449, 468, 493, 499), and the requirements template's own self-description (`requirements-template.md:3`, "Canonical handoff file: **`01-requirements.md`**") — is `01-requirements.md`. No file named bare `requirements.md` exists or is ever produced by the workflow.
- **Why it matters:** Low impact — the surrounding SKILL.md prose and agent-def inboxes all use the correct numbered name, so a gate is unlikely to actually go looking for a nonexistent `requirements.md`. But `design-interface-template.md`'s occurrence is inside the **Traceability** section boilerplate, which is carried verbatim into the real, promoted `02-design-interface.md` handoff file for every feature unless the conductor happens to edit that parenthetical — so the wrong filename can ship into an actual artifact repeatedly, not just live in a reference doc.
- **Recommendation (advisory):** Change both occurrences to `01-requirements.md` for consistency with every other reference to this file in the repo.
- **Status:** fixed — both occurrences changed to `01-requirements.md`.

### m-13
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 7
- **Location:** `CLAUDE.md` ("(3) **secrets guardrail** … (4) **test-integrity**" — enumerated as four numbered jobs, no fifth), `docs/developer-guide.md:180-190` ("Four jobs: 1. Audit … 2. Secrets guardrail … 3. Algorithm-blind … 4. Test-integrity"), and `docs/tutorial.md:237-243` ("does the cross-cutting work … (a) audits … (b) denies secrets … (c) denies the test-writer … (d) denies the implementer editing any test file") — three independent canonical docs, all enumerating the same four denials.
- **Claim vs. reality:** Per Unit 4 (`guard.py:222`, tested at `test_guard.py:71`), the guard actually enforces a **fifth** denial — draft-confinement: any subagent is denied reading under `handoff/draft/`, which `SKILL.md:112-123` does list. All three top-level/developer-facing docs independently omit it, describing only four jobs.
- **Why it matters:** Confirmed real behavior (not a false guarantee — Unit 4 resolved that scare), but three separate canonical entry points into the architecture (the project's own CLAUDE.md, the Developer Guide, and the Tutorial) all undercount the guard's actual job list identically, suggesting the four-job phrasing was copied forward rather than each doc independently checked against `guard.py`. A developer reading any one of these and then extending the guard would not know draft-confinement exists as a precedent to preserve.
- **Recommendation (advisory):** Add draft-confinement as job (e) in all three locations, matching `SKILL.md`'s five-item list.
- **Status:** fixed — added draft-confinement as the fifth guard job in CLAUDE.md, developer-guide.md, and tutorial.md.

### m-14
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 7
- **Location:** `CLAUDE.md` ("every Read/Bash/Grep/Glob/Edit/Write"), `docs/developer-guide.md:178` ("on every `Read`/`Bash`/`Grep`/`Glob`/`Edit`/`Write`"), `docs/tutorial.md:238` ("on every `Read`/`Bash`/`Grep`/`Glob`/`Edit`/`Write`") — three docs, identical tool enumeration, all omitting `NotebookEdit`.
- **Claim vs. reality:** `hooks.json:5`'s matcher includes `NotebookEdit`, and Unit 4 confirmed `guard.py`'s `WRITEISH` set (`guard.py:103`) covers it for test-integrity and reviewer-confinement — real coverage, just never named in prose. Same class of omission as `guard.py`'s own docstring (N-03), now shown to be a repo-wide pattern, not a one-off.
- **Why it matters:** Purely descriptive gap — enforcement is unaffected — but a reader relying on any of these three docs to know the guard's matched-tool surface would list one tool short everywhere they look.
- **Recommendation (advisory):** Add `NotebookEdit` to all three enumerations (and `guard.py`'s docstring per N-03) in one pass.
- **Status:** fixed — added `NotebookEdit` to the tool enumeration in CLAUDE.md, developer-guide.md, and tutorial.md.

### m-15
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 7
- **Location:** `docs/developer-guide.md:105,108` — handoff-contract table: `| IMPLEMENT [I] | tests + full design | <code_root>/… |` (omits `01-requirements.md`) and `| VERIFY [I] | \`01-requirements\` (ACs + boundary inventory) | \`07-verify-report\` |` (omits `<code_root>/`).
- **Claim vs. reality:** This is the same table structure and the same two omissions found in `SKILL.md` (M-02/m-04 for the IMPLEMENT row's missing `01-requirements.md`; m-01 for the VERIFY row's missing `<code_root>/`), now shown to be duplicated verbatim in the Developer Guide's own summary of the handoff contract — a third and fourth occurrence of each respective omission (SKILL table, SKILL prose, dev-guide table).
- **Why it matters:** Confirms the M-02/m-04/m-01 drift is not confined to `SKILL.md` — it was copied into the Developer Guide's architecture summary too, which a developer is at least as likely to trust as the canonical `SKILL.md` gate prose (which does get `<code_root>/` right for VERIFY, per m-01's own text). Low functional risk (the agent-defs are correct per Unit 3), but it means **any** fix to M-02/m-04/m-01 must also touch this table or the drift will look "fixed" in one doc and persist in another.
- **Recommendation (advisory):** Fix alongside M-02/m-04/m-01: add `01-requirements.md` to the IMPLEMENT row and `<code_root>/` to the VERIFY row of `developer-guide.md`'s handoff table.
- **Status:** fixed — alongside m-04/m-01, added `01-requirements.md` to the IMPLEMENT row and `<code_root>/` to the VERIFY row of developer-guide.md's handoff table.

### m-16
- **Severity:** Minor
- **Frame:** 1 (internal consistency)
- **Unit:** 7
- **Location:** `docs/user-guide.md:147` — Gate 1 row of the "Running a feature" table: "Writes a `requirements.md` draft for you to read."
- **Claim vs. reality:** Same wrong-filename class as m-12 (`quality-standards.md:82`, `design-interface-template.md:28`) — the canonical handoff filename used everywhere else, including this same table's own later gates and `requirements-template.md`'s self-description, is `01-requirements.md`. No file named bare `requirements.md` is ever produced. This is now a **fourth** occurrence of the same bug across the repo.
- **Why it matters:** Unlike m-12's occurrences (an internal reference doc and boilerplate carried into an artifact), this one is in the **User Guide** — the doc a real, non-repo-familiar stranger reads to know what to expect. A user grepping their `.implement-feature/<run>/handoff/` for `requirements.md` per this doc would find nothing by that name.
- **Recommendation (advisory):** Change to `01-requirements.md` here too; consider a single repo-wide grep-and-fix pass for `requirements.md` (bare) given four independent occurrences (m-12 ×2, this one, and any others a full grep would find) all trace to the same drift.
- **Status:** fixed — changed to `01-requirements.md`.

### N-04
- **Severity:** Nit
- **Frame:** 1 (internal consistency)
- **Unit:** 7
- **Location:** `DEVCONTAINER.md:19` — "Run these **on the Mac**, from the repo root (`~/dev/expt-skill-wotkflow-agent`)."
- **Claim vs. reality:** Typo — "wotkflow" for "workflow." The actual repo directory name (confirmed via `git remote -v`: `Sdaas/expt-skill-workflow-agent`) is `expt-skill-workflow-agent`.
- **Why it matters:** Purely cosmetic; a reader would still find the repo by context.
- **Recommendation (advisory):** Fix the typo.
- **Status:** resolved — the repo-rename pass (`Update stale repo-name references after rename to sdlc-lite`) already fixed this line to `~/dev/sdlc-lite`; no separate action needed.

### N-05
- **Severity:** Nit
- **Frame:** 1 (internal consistency)
- **Unit:** 7
- **Location:** `docs/tutorial.md:152` (`/plugin marketplace add /workspaces/expt-skill-workflow-agent` — the interactive slash-command form) vs the same doc's own stated rule at `docs/tutorial.md:113-115` ("Prefer the CLI installer for deterministic installs — typing `/plugin install X@Y` as a session one-liner can just open the manager UI and no-op") and `docs/user-guide.md:44-50`, which uses the CLI form (`claude plugin marketplace add …`) for both `marketplace add` and `install`.
- **Claim vs. reality:** The tutorial's runnable example uses the slash-command one-liner for `marketplace add` but then switches to the CLI form for `install` on the very next line (`claude plugin install toy-greet@daas-plugins`) — while its own stated rule and the User Guide's practice both use the CLI form throughout. It's not demonstrably wrong (the warning is scoped to `install`), but the example is inconsistent with the more conservative pattern used everywhere else in the repo.
- **Why it matters:** Low impact — a reader following the tutorial's exact commands would likely succeed — but a reader who generalizes "the CLI form is safer" from §5 and then sees the tutorial use the slash form for `marketplace add` a few sections later may reasonably wonder if that one is exempt for a real reason (it isn't stated either way).
- **Recommendation (advisory):** Use the CLI form (`claude plugin marketplace add /workspaces/expt-skill-workflow-agent`) in the tutorial example too, for consistency with §5's own advice and the User Guide.
- **Status:** fixed — tutorial.md now uses the CLI form for `marketplace add`, consistent with its own stated rule and the User Guide.

### m-17
- **Severity:** Minor
- **Frame:** 1 (internal consistency) — Scope: tracked-scaffolding flag
- **Unit:** 7
- **Location:** `REFACTOR-PLAN.md` (502 lines, repo root) and `RESUME.md` (86 lines, repo root) — both `git ls-files`-tracked, neither matched by `.gitignore` (`grep -n "REFACTOR-PLAN\|RESUME.md" .gitignore` returns nothing).
- **Claim vs. reality:** Per REVIEW-PROMPT's Scope section, these are process/refactor scaffolding (not part of the shipped product a stranger installs) and should be flagged if tracked-and-shouldn't-be. Both are substantial (588 combined lines) and remain committed at what README.md's Status section calls a **v1** shipped state.
- **Why it matters:** A stranger cloning the repo per the User Guide's install instructions sees two large, refactor-session-specific planning documents at the root alongside `README.md`/`CLAUDE.md`/`DEVCONTAINER.md` — noise unrelated to using or understanding the product, and a maintainer signal that these were meant to be transient working state, not shipped documentation (per this repo's own `CLAUDE.md`: "Temp/scratch files go to `/tmp/` or end in `.tmp`, deleted when done" — a looser version of that same discipline would argue for removing or gitignoring these once the refactor phases they describe are complete).
- **Recommendation (advisory):** If the refactor they document is finished (recent commits suggest Phase 5 is done), either delete them, move their durable content into `docs/developer-guide.md`'s ADRs (where the load-bearing lessons already migrated per that doc's §6 header), or gitignore them for future refactor sessions so they don't linger in a "shipped" tree.
- **Status:** open
