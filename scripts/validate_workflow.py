#!/usr/bin/env python3
"""Local validation for the zero-budget n8n missed-call recovery demo."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WF=ROOT/'AIStar.YOU_Missed_Call_Demo_V1.json'
FX=ROOT/'tests/fixtures/hvac_missed_call_fixtures.json'
REQUIRED_NODES={
 'Webhook','Normalize Missed Call Payload','Required Data Check',
 'Consent Opt-Out Suppression Eligibility Check','Deterministic Demo Duplicate Check',
 'Execution History Duplicate Flag','Execution History Duplicate Check',
 'Remove Duplicates','Build Simulated Recovery Records','Build Blocked Eligibility Result',
 'Build Duplicate Result','Build Invalid Payload Result','Final Structured Webhook Response'}
REQUIRED_FIXTURES={'ready_for_handoff','opt_out','suppressed_contact','unapproved_consent','duplicate_lead','malformed_missing_required_data','human_review_required','urgent_human_review_required'}
REQUIRED_HANDOFF_STATUSES={'READY_FOR_HANDOFF','HUMAN_REVIEW_REQUIRED','URGENT_HUMAN_REVIEW_REQUIRED'}
URGENT_TERMS=['emergency','urgent','asap','immediate','gas smell','carbon monoxide','sparks','smoke','flooding','burst pipe','electrical hazard','medical','elderly','infant','no heat with freezing','water pouring']
AMBIGUOUS_TERMS=['not sure','unknown','unclear','maybe','something wrong','issue','problem','help','?']
CATEGORY_ONLY={'no_cooling','no_heat','water_leak'}
PROHIBITED=[r'AC[a-zA-Z0-9_\-]{20,}',r'SK[a-zA-Z0-9_\-]{20,}',r'AIza[0-9A-Za-z_\-]{20,}',r'xox[baprs]-[0-9A-Za-z-]+']

def fail(msg): print(f'FAIL: {msg}'); sys.exit(1)
def expected_handoff(body):
    urgent_blob=' '.join(str(body.get(k,'')).lower() for k in ('customer_message','service_requested','urgency'))
    detail_blob=' '.join(str(body.get(k,'')).lower() for k in ('customer_message','service_requested'))
    urgent=any(t in urgent_blob for t in URGENT_TERMS)
    ambiguous=len(str(body.get('customer_message','')).strip()) < 20 or any(t in detail_blob for t in AMBIGUOUS_TERMS)
    if urgent: return 'URGENT_HUMAN_REVIEW_REQUIRED', True
    if ambiguous: return 'HUMAN_REVIEW_REQUIRED', True
    return 'READY_FOR_HANDOFF', False
workflow=json.loads(WF.read_text())
fixtures=json.loads(FX.read_text())
wf_text=WF.read_text()
fx_text=FX.read_text()
if workflow.get('active') is not False: fail('workflow must remain inactive for import/testing')
names={n.get('name') for n in workflow.get('nodes',[])}
missing=REQUIRED_NODES-names
if missing: fail(f'missing required nodes: {sorted(missing)}')
conn=workflow.get('connections',{})
for src,dst in [('Webhook','Normalize Missed Call Payload'),('Normalize Missed Call Payload','Required Data Check'),('Execution History Duplicate Flag','Execution History Duplicate Check'),('Execution History Duplicate Check','Build Duplicate Result'),('Execution History Duplicate Check','Remove Duplicates'),('Remove Duplicates','Build Simulated Recovery Records')]:
    if dst not in json.dumps(conn.get(src,{})): fail(f'missing connection {src} -> {dst}')
node_by_name={n.get('name'): n for n in workflow.get('nodes',[])}
remove_duplicates_operation=node_by_name['Remove Duplicates'].get('parameters',{}).get('operation')
if remove_duplicates_operation != 'removeDuplicateInputItems': fail('Remove Duplicates must not drop prior-execution webhook items before a response is returned')
for field in ('handoff_status','human_review_required','handoff_reason','alert_priority','city','zip','urgency','callback_preference'):
    if field not in wf_text: fail(f'required BW-003 field missing from workflow: {field}')
for status in REQUIRED_HANDOFF_STATUSES:
    if status not in wf_text + fx_text: fail(f'missing handoff status: {status}')
if "['gas_smell','no_heat','no_cooling','water_leak']" in wf_text or "['no_cooling','no_heat','water_leak','gas_smell']" in wf_text:
    fail('old category-only urgency/qualification list remains in workflow')
if 'duplicate_lead_execution_history' not in wf_text: fail('execution-history duplicate response reason missing')
for pat in PROHIBITED:
    if re.search(pat,wf_text+fx_text): fail(f'prohibited secret-like token matched {pat}')
if 'hello@aistar.you' not in wf_text+fx_text: fail('simulated owner-alert destination missing')
if 'simulated' not in (wf_text+fx_text).lower() or 'not sent' not in (wf_text+fx_text).lower(): fail('simulation/not-sent labels missing')
fixture_names={f.get('name') for f in fixtures.get('fixtures',[])}
missing_fx=REQUIRED_FIXTURES-fixture_names
if missing_fx: fail(f'missing fixtures: {sorted(missing_fx)}')
expected_fixture_statuses=set()
for f in fixtures['fixtures']:
    b=f.get('body',{})
    if b.get('test_mode') is not True: fail(f"fixture {f.get('name')} must keep test_mode true")
    if f.get('expected_handoff_status'):
        status,review=expected_handoff(b)
        if f['expected_handoff_status'] != status: fail(f"fixture {f['name']} expected handoff mismatch: {f['expected_handoff_status']} vs deterministic {status}")
        if f.get('expected_human_review_required') is not review: fail(f"fixture {f['name']} human_review_required mismatch")
        expected_fixture_statuses.add(status)
        print(f'PASS: fixture {f["name"]} -> {status}, human_review_required={review}')
ready=next(f for f in fixtures['fixtures'] if f['name']=='ready_for_handoff')
if ready['body'].get('event_id')!='DEMO-HVAC-001': fail('ready_for_handoff fixture must use DEMO-HVAC-001')
if ready['body'].get('issue_category') in CATEGORY_ONLY and ready.get('expected_handoff_status')!='READY_FOR_HANDOFF': fail('category-only HVAC fixture must not be urgent')
if REQUIRED_HANDOFF_STATUSES-expected_fixture_statuses: fail('fixtures do not prove all three BW-003 handoff statuses')
print(f'PASS: {WF.name} JSON is valid with {len(workflow["nodes"])} nodes')
print('PASS: required nodes and core connections are present')
print('PASS: deterministic BW-003 handoff statuses and fixtures are present')
print('PASS: category-only no_cooling/no_heat/water_leak urgency logic is absent')
print('PASS: no prohibited secret patterns found')
print(f'PASS: {len(fixtures["fixtures"])} controlled HVAC fixtures are present')
