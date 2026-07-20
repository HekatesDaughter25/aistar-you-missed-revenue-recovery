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
 'Remove Duplicates','Build Simulated Recovery Records','Build Blocked Eligibility Result',
 'Build Duplicate Result','Build Invalid Payload Result','Final Structured Webhook Response'}
REQUIRED_FIXTURES={'eligible_lead','opt_out','suppressed_contact','unapproved_consent','duplicate_lead','malformed_missing_required_data'}
PROHIBITED=[r'AC[a-zA-Z0-9_\-]{20,}',r'SK[a-zA-Z0-9_\-]{20,}',r'AIza[0-9A-Za-z_\-]{20,}',r'xox[baprs]-[0-9A-Za-z-]+']

def fail(msg): print(f'FAIL: {msg}'); sys.exit(1)
workflow=json.loads(WF.read_text())
fixtures=json.loads(FX.read_text())
if workflow.get('active') is not False: fail('workflow must remain inactive for import/testing')
names={n.get('name') for n in workflow.get('nodes',[])}
missing=REQUIRED_NODES-names
if missing: fail(f'missing required nodes: {sorted(missing)}')
conn=workflow.get('connections',{})
for src,dst in [('Webhook','Normalize Missed Call Payload'),('Normalize Missed Call Payload','Required Data Check'),('Remove Duplicates','Build Simulated Recovery Records')]:
    blob=json.dumps(conn.get(src,{}))
    if dst not in blob: fail(f'missing connection {src} -> {dst}')
text=WF.read_text()+FX.read_text()
for pat in PROHIBITED:
    if re.search(pat,text): fail(f'prohibited secret-like token matched {pat}')
if 'hello@aistar.you' not in text: fail('simulated owner-alert destination missing')
if 'simulated' not in text.lower() or 'not sent' not in text.lower(): fail('simulation/not-sent labels missing')
fixture_names={f.get('name') for f in fixtures.get('fixtures',[])}
missing_fx=REQUIRED_FIXTURES-fixture_names
if missing_fx: fail(f'missing fixtures: {sorted(missing_fx)}')
for f in fixtures['fixtures']:
    b=f.get('body',{})
    if b.get('test_mode') is not True: fail(f"fixture {f.get('name')} must keep test_mode true")
print(f'PASS: {WF.name} JSON is valid with {len(workflow["nodes"])} nodes')
print(f'PASS: required nodes and core connections are present')
print(f'PASS: no prohibited secret patterns found')
print(f'PASS: {len(fixtures["fixtures"])} controlled HVAC fixtures are present')
