---
description: Toy 2-gate workflow that composes a personalized greeting with human approval gates.
---

# /greet — a 2-gate greeting workflow

You are running the **greet** workflow. Follow these phases IN ORDER. Do not skip a gate.

## Phase 1 — Collect (ask)
Ask the user two things, one message:
1. Who is the greeting for (a name)?
2. What tone do they want (e.g. formal, casual, playful)?

If either answer is missing or unclear, ask again. Do not proceed until you have both.

## GATE 1 — Confirm inputs (human approval)
Echo back what you captured:

> "I'll write a **{tone}** greeting for **{name}**. Shall I draft it? (reply APPROVED or tell me what to change)"

**STOP. Do not draft anything until the user replies APPROVED.** If they request changes, apply
them and re-confirm at this same gate.

## Phase 2 — Draft (act)
Compose a 1–2 sentence greeting for {name} in the {tone} tone. Show it to the user.

## GATE 2 — Approve final (human approval)
Ask:

> "Here's the greeting. Reply APPROVED to finish, or tell me what to adjust."

**STOP. Do not declare the workflow complete until the user replies APPROVED.** On changes,
revise and return to this gate.

## Done
When GATE 2 is approved, present the final greeting and state that the workflow is complete.
