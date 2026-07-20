# AIStar.YOU Missed Revenue Recovery — Zero-Budget HVAC V1 Demo

AIStar.YOU Missed Revenue Recovery is a consent-aware n8n demonstration workflow for HVAC missed-call recovery. The V1 demo shows the internal decision process a production system would use before any outreach: normalize a simulated missed-call webhook, enforce consent and suppression protections, remove duplicates, qualify the lead with deterministic rules, create simulated records, and return a structured webhook response.

This repository is intentionally honest about boundaries: it does **not** send SMS, does **not** send email, does **not** call Gemini or another paid AI API, does **not** book calendar appointments, and does **not** claim recovered revenue or real customer outcomes.

## Problem

HVAC companies can miss high-intent calls when a dispatcher is busy, a call arrives after hours, or a technician is on another job. A production missed-call recovery system could help by rapidly identifying qualified leads and preparing compliant follow-up. However, live outreach requires consent controls, opt-out handling, suppression checks, duplicate protection, and verified delivery integrations.

## V1 Solution

The V1 workflow demonstrates the complete internal decision path without paid services or live delivery. It uses controlled webhook payloads and deterministic HVAC rules to produce:

- a lead qualification result;
- an urgency classification;
- a simulated customer-response record clearly labeled as not sent;
- a simulated owner-alert record addressed to `hello@aistar.you` and clearly labeled as not sent;
- audit fields describing the zero-budget simulation boundary;
- a final structured webhook response.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `AIStar.YOU_Missed_Call_Demo_V1.json` | Current importable n8n V1 workflow. |
| `docs/AIStar.YOU_Missed_Call_Demo_V1_original_export.json` | Original exported workflow retained for comparison. |
| `tests/fixtures/hvac_missed_call_fixtures.json` | Controlled HVAC webhook payload fixtures. |
| `scripts/validate_workflow.py` | Local validation script; no network or paid services required. |

## Present Behavior Reviewed From the Original Export

The original workflow contained five nodes:

1. `Webhook` accepted a `POST` request at `missed-call`.
2. `Edit Fields` normalized selected webhook body fields into top-level fields.
3. `If` checked whether `consent_status` was `approved_test`, `opt_out` was `false`, and `suppression_status` was `clear`.
4. `Remove Duplicates` attempted to remove already-seen eligible leads using `lead_id`.
5. `Edit Fields1` created a blocked result with a basic `eligibility_reason` for failed eligibility checks.

That export did not yet finish the eligible branch after duplicate removal, did not return final webhook responses, did not include controlled fixtures beyond pinned sample data, and did not include local validation.

## Current Workflow Architecture

The current V1 keeps the original intent and extends it into a full demonstration:

1. `Webhook` receives a simulated missed-call event and uses n8n's response-node mode.
2. `Normalize Missed Call Payload` maps webhook body fields into workflow fields and adds the V1 workflow version.
3. `Required Data Check` stops malformed payloads or payloads where `test_mode` is not true.
4. `Consent Opt-Out Suppression Eligibility Check` preserves consent, opt-out, and suppression protections.
5. `Build Blocked Eligibility Result` creates a structured stopped result when a contact is opted out, suppressed, or lacks approved test consent.
6. `Deterministic Demo Duplicate Check` provides a controlled duplicate fixture guard for repeatable local demos.
7. `Execution History Duplicate Flag` checks persisted demo duplicate state before the item can be dropped by n8n duplicate removal.
8. `Execution History Duplicate Check` routes previously seen eligible demo keys to a structured duplicate result.
9. `Remove Duplicates` remains in the fresh eligible path to remove duplicate items within the current execution without swallowing the only webhook response item.
10. `Build Duplicate Result` returns a structured stopped result for both the controlled duplicate fixture and execution-history duplicates.
11. `Build Invalid Payload Result` returns a structured stopped result for malformed or incomplete input.
12. `Build Simulated Recovery Records` deterministically qualifies eligible HVAC leads, classifies urgency, and builds simulated customer and owner records.
13. `Final Structured Webhook Response` returns the final JSON response to the webhook caller.

## Consent and Safety Protections

The workflow is designed to stop before any simulated outreach record is created unless all of these are true:

- `test_mode` is true;
- required fields are present;
- `consent_status` is `approved_test`;
- `opt_out` is false;
- `suppression_status` is `clear`;
- the demo duplicate guard does not identify the fixture as duplicate;
- the execution-history duplicate check has not already seen the demo key;
- the current execution duplicate-removal node allows the fresh item through.

Blocked and invalid branches explicitly state that no live delivery was attempted.

## Zero-Budget Simulation Boundaries

V1 is a demonstration only:

- Twilio SMS is **not implemented**. The customer response is a simulated record for future Twilio production work only.
- Email delivery is **not implemented**. The owner alert is a simulated record addressed to `hello@aistar.you`; it does not claim a live email was delivered.
- Gemini, OpenAI, or other AI API calls are **not implemented**. Lead qualification and urgency classification use deterministic rules.
- Calendar booking is **outside V1** and is not implemented.
- Customer-facing message text is labeled simulated and not approved for live sending.
- The workflow uses sample numbers and does not require the founder's phone number.

## Setup and n8n Import

1. Open n8n.
2. Import `AIStar.YOU_Missed_Call_Demo_V1.json`.
3. Keep the workflow inactive unless you are intentionally testing it.
4. Use the n8n test webhook URL for `POST /missed-call` testing.
5. Send fixture bodies from `tests/fixtures/hvac_missed_call_fixtures.json` as JSON payloads.
6. Do not add credentials for Twilio, email, calendar, Gemini, or any other external service for V1.

## Test Procedure and Expected Outputs

Run local validation first:

```bash
./scripts/validate_workflow.py
```

Expected local validation output includes four `PASS` lines confirming JSON validity, required nodes/connections, absence of secret-like tokens, and six controlled fixtures.

In n8n, test each fixture body:

| Fixture | Expected status | Expected notes |
| --- | --- | --- |
| `eligible_lead` | `completed_simulation` | Produces deterministic qualification, urgency, simulated customer response, and simulated owner alert. |
| `opt_out` | `stopped` | Stops with `opt_out`; no simulated customer response or live delivery. |
| `suppressed_contact` | `stopped` | Stops with `suppressed`; no simulated customer response or live delivery. |
| `unapproved_consent` | `stopped` | Stops with `consent_not_approved`; no simulated customer response or live delivery. |
| `duplicate_lead` | `stopped` | Stops with `duplicate_lead_demo_guard` using the controlled fixture key. Replayed eligible keys stop with `duplicate_lead_execution_history`. |
| `malformed_missing_required_data` | `stopped` | Stops with `malformed_or_missing_required_data_or_test_mode_not_true`. |

## Current Limitations

- n8n import and execution must still be manually verified inside an n8n instance.
- Execution-history duplicate detection uses n8n workflow static data so replayed eligible demo keys return a structured stopped response instead of being silently dropped; `Remove Duplicates` is limited to duplicate items inside the current execution to avoid hanging response-node webhooks.
- No live owner email, SMS, voice call, AI classification, CRM update, or calendar booking occurs.
- The workflow does not prove recovered revenue, booked jobs, delivery confirmation, or customer conversion.

## Future Production Integrations — Not Implemented in V1

The following are possible future production requirements, but they are not implemented in this repository:

- Twilio SMS sending with verified opt-in, STOP handling, delivery status callbacks, and compliance review.
- Owner email delivery through a configured transactional email provider.
- CRM lead creation or update.
- Calendar availability checks and booking.
- Human-approved AI drafting or classification after billing, quota, privacy, and reliability requirements are met.
- Persistent suppression-list and duplicate-state storage beyond n8n execution history.

## How Codex Was Used

Codex was used as the engineering agent to inspect the original n8n export, preserve its working consent/eligibility and duplicate-removal structure, extend the workflow with deterministic zero-budget branches, add controlled fixtures, write a local validation script, run local checks, and document the demo boundaries. Codex did not add credentials, API keys, secrets, personal data, live-delivery integrations, or claims of real delivery/revenue.
