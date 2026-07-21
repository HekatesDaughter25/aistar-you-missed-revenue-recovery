# BW-003 Codex Task — Implement Deterministic Qualification and Handoff

Implement `docs/BW-003_IMPLEMENTATION_SPEC.md` on branch `bw-003-deterministic-handoff`.

## Scope
Make the smallest possible change on top of current `main`.

Do **not** rebuild or remove the already-merged foundations:
- webhook normalization
- required-data gate
- consent / opt-out / suppression protection
- deterministic demo duplicate guard
- execution-history duplicate handling
- `Remove Duplicates`
- simulated customer-response record
- simulated owner-alert record
- final structured webhook response
- existing zero-budget / no-live-delivery boundary

## Required final handoff outcomes
Every fresh eligible lead that reaches the qualification/handoff stage must deterministically produce exactly one of:

1. `READY_FOR_HANDOFF`
2. `HUMAN_REVIEW_REQUIRED`
3. `URGENT_HUMAN_REVIEW_REQUIRED`

Add explicit structured fields for the final handoff decision, including at minimum:
- `handoff_status`
- `human_review_required`
- `handoff_reason`
- alert priority appropriate to the branch

The final webhook response must expose the handoff result.

## Mandatory happy path
`DEMO-HVAC-001` must return:
- `handoff_status = READY_FOR_HANDOFF`
- `human_review_required = false`
- service need: upstairs AC stopped cooling; system running but air feels warm
- city: Frisco
- ZIP: 75034
- urgency: today
- callback preference: as soon as someone is available
- normal/non-priority simulated owner/dispatcher alert

Do **not** infer diagnosis, price, appointment, availability, emergency service, or safety guidance.

A `no_cooling` service category by itself must **not** trigger urgent classification.

## Human review path
Create a controlled fixture that returns `HUMAN_REVIEW_REQUIRED` for unclear, ambiguous, incomplete, or unsafe-to-interpret job information.

The workflow must route it to human review without autonomous resolution.

## Urgent human review path
Create a controlled fixture that returns `URGENT_HUMAN_REVIEW_REQUIRED` only when the payload contains explicit urgent/concerning content defined conservatively in the implementation spec.

Produce a PRIORITY simulated owner/dispatcher alert.

Do not diagnose, provide safety instructions, or promise emergency service.

## Deterministic rule constraint
Remove the current broad behavior that automatically treats `no_cooling`, `no_heat`, or `water_leak` as high urgency merely because of service category.

Urgent status must require explicit concerning/urgent content or an explicitly approved deterministic signal.

## Files expected to change
Prefer only the minimum necessary files, likely:
- `AIStar.YOU_Missed_Call_Demo_V1.json`
- `tests/fixtures/hvac_missed_call_fixtures.json`
- `scripts/validate_workflow.py`
- `README.md`

Do not add paid services, credentials, live SMS, live email, AI API calls, calendar booking, CRM integrations, or production claims.

## Validation requirements
Update the validator so it fails unless:
- all three handoff statuses exist in the workflow/fixtures
- `DEMO-HVAC-001` expects `READY_FOR_HANDOFF`
- a human-review fixture exists
- an urgent-human-review fixture exists
- old category-only high-urgency logic is removed
- existing safety/duplicate nodes and paths remain present
- zero-budget/no-live-delivery labels remain present
- no prohibited secret patterns are introduced

Run local validation and JSON syntax checks.

## Completion report
When finished, report:
1. exact files changed
2. exact deterministic handoff rules implemented
3. validator output
4. JSON syntax-check results
5. any remaining n8n runtime verification still required

Do not merge to `main`. Leave the branch reviewable for runtime verification first.
