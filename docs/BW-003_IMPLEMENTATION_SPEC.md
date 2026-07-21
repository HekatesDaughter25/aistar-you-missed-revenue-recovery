# BW-003 — Deterministic Qualification and Handoff Rules

Status: IN PROGRESS
Branch: `bw-003-deterministic-handoff`
Baseline: current `main` after merged PR #1

## Scope

Implement only the missing deterministic qualification and handoff decision model. Preserve all existing consent, opt-out, suppression, duplicate, simulated customer-response, simulated owner-alert, webhook-response, fixture, and zero-budget simulation protections.

## Approved handoff outcomes

### 1. `READY_FOR_HANDOFF`
Use when the structured lead is sufficiently complete and interpretable, there is no explicit urgent/concerning content, and `human_review_required` is false.

Result requirements:
- `handoff_status = READY_FOR_HANDOFF`
- normal simulated owner/dispatcher alert priority
- structured handoff record
- no diagnosis
- no binding price
- no appointment promise
- no availability promise
- no safety instructions

### 2. `HUMAN_REVIEW_REQUIRED`
Use for normal exceptions such as unclear information, missing or ambiguous job details, or content that the automation cannot safely interpret.

Result requirements:
- `handoff_status = HUMAN_REVIEW_REQUIRED`
- `human_review_required = true`
- simulated owner/dispatcher alert clearly marked for human review
- automation does not diagnose, price, promise appointments, or autonomously resolve ambiguity

### 3. `URGENT_HUMAN_REVIEW_REQUIRED`
Use only when the payload contains explicit urgent or concerning content.

Result requirements:
- `handoff_status = URGENT_HUMAN_REVIEW_REQUIRED`
- `human_review_required = true`
- simulated owner/dispatcher alert marked PRIORITY
- automation does not diagnose
- automation gives no safety instructions
- automation does not promise emergency service or availability

## Critical deterministic rule

Do **not** infer urgency solely from a service category.

The previous broad rule that automatically treated `no_cooling`, `no_heat`, or `water_leak` as high urgency must be removed.

Urgent classification must require explicit urgent/concerning content in controlled input fields. Service category alone is not enough.

## Approved happy-path fixture

`DEMO-HVAC-001` must resolve to `READY_FOR_HANDOFF`.

Approved structured interpretation:
- service need: `Upstairs AC stopped cooling; system is running but air feels warm`
- city: `Frisco`
- ZIP: `75034`
- urgency: `today`
- callback preference: `as soon as someone is available`
- `human_review_required = false`
- `handoff_status = READY_FOR_HANDOFF`

Do not infer diagnosis, price, appointment, technician availability, or safety guidance.

## Controlled evidence fixtures required

Maintain existing fixtures and add or update controlled fixtures that prove all three handoff outcomes:

1. `ready_for_handoff` — maps to `READY_FOR_HANDOFF`
2. `human_review_required` — ambiguous/incomplete non-urgent content maps to `HUMAN_REVIEW_REQUIRED`
3. `urgent_human_review_required` — explicit urgent/concerning content maps to `URGENT_HUMAN_REVIEW_REQUIRED`

Existing opt-out, suppression, consent, duplicate, malformed-payload, and execution-history duplicate protections must remain unchanged.

## Structured response requirements

The final webhook response for eligible processed leads must expose, at minimum:
- `workflow_status`
- `lead_id`
- `eligibility_decision`
- `qualification_result`
- `handoff_status`
- `human_review_required`
- `urgency_classification`
- `simulated_customer_response_record`
- `simulated_owner_alert_record`
- audit/simulation-boundary fields

## Owner/dispatcher alert behavior

- `READY_FOR_HANDOFF` → normal simulated alert
- `HUMAN_REVIEW_REQUIRED` → simulated alert clearly requesting human review
- `URGENT_HUMAN_REVIEW_REQUIRED` → PRIORITY simulated alert requesting urgent human review

All alerts remain simulation-only and not sent.

## Definition of done

BW-003 is complete only when:
1. The workflow contains the three approved deterministic handoff outcomes.
2. `DEMO-HVAC-001` returns `READY_FOR_HANDOFF`.
3. A controlled non-urgent ambiguous fixture returns `HUMAN_REVIEW_REQUIRED`.
4. A controlled explicit urgent/concerning fixture returns `URGENT_HUMAN_REVIEW_REQUIRED`.
5. Existing consent, opt-out, suppression, duplicate, invalid-payload, and zero-budget simulation protections still work.
6. Validator coverage is updated for the new rules/fixtures.
7. README is updated to describe the final handoff model truthfully.
8. Local validation passes before runtime n8n verification.

## Evidence required before merge

- changed-file list
- validation output
- three controlled handoff fixture results
- n8n runtime output for the three handoff paths
- confirmation that no live SMS/email/API/booking integration was added

Do not merge until runtime evidence is reviewed.