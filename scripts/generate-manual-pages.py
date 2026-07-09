#!/usr/bin/env python3
"""
Generate Mintlify manual API pages from openapi.json.
Focused on integration partner capabilities:
  - KYC Verification (history, individual standard/advanced, business, custom)
  - Document Authenticity
  - Voice Intelligence
  - Claims Management
  - Evidence Management
  - Participants & Sanctions
"""
import json, os, re

SPEC = json.load(open('api-reference/openapi.json'))

# (method, path, group-dir, slug)
ENDPOINTS = [
    # ── Authentication ──────────────────────────────────────────────────────
    ('post', '/api/v1/auth/login',   'authentication', 'login'),
    ('post', '/api/v1/auth/refresh', 'authentication', 'refresh'),
    ('get',  '/api/v1/auth/me',      'authentication', 'me'),

    # ── KYC Verification ────────────────────────────────────────────────────
    ('post', '/api/v1/kyc/verifications',                      'kyc', 'create-verification'),
    ('get',  '/api/v1/kyc/verifications',                      'kyc', 'list-verifications'),
    ('get',  '/api/v1/kyc/verifications/by-participant',       'kyc', 'by-participant'),
    ('get',  '/api/v1/kyc/verifications/all',                  'kyc', 'list-all'),
    ('get',  '/api/v1/kyc/verifications/{id}',                 'kyc', 'get-verification'),
    ('get',  '/api/v1/kyc/verifications/{id}/status',          'kyc', 'verification-status'),
    ('post', '/api/v1/kyc/verifications/{id}/poll',            'kyc', 'poll-verification'),
    ('post', '/api/v1/kyc/verifications/{id}/retry',           'kyc', 'retry-verification'),
    ('post', '/api/v1/kyc/verifications/{id}/documents',       'kyc', 'upload-documents'),
    ('post', '/api/v1/kyc/verifications/{id}/approve',         'kyc', 'approve-verification'),
    ('post', '/api/v1/kyc/verifications/{id}/sync',            'kyc', 'sync-verification'),

    # ── Document Authenticity ────────────────────────────────────────────────
    ('post', '/api/v1/documents/verification/upload-and-process',          'document-verification', 'upload-and-process'),
    ('post', '/api/v1/documents/verification',                             'document-verification', 'create-session'),
    ('post', '/api/v1/documents/verification/{verificationId}/upload',     'document-verification', 'upload-file'),
    ('post', '/api/v1/documents/verification/{verificationId}/process',    'document-verification', 'process'),
    ('get',  '/api/v1/documents/verification/history',                     'document-verification', 'history'),
    ('get',  '/api/v1/documents/verification/{verificationId}',            'document-verification', 'get-session'),
    ('get',  '/api/v1/documents/verification/{verificationId}/report',     'document-verification', 'get-report'),
    ('post', '/api/v1/documents/verification/vehicle',                     'document-verification', 'verify-vehicle-doc'),
    ('get',  '/api/v1/documents/verification/vehicle/{verificationId}',    'document-verification', 'get-vehicle-result'),
    ('post', '/api/v1/documents/verification/custom',                      'document-verification', 'custom-verification'),
    ('post', '/api/v1/documents/verification/kra-pin',                     'document-verification', 'verify-kra-pin'),
    ('get',  '/api/v1/documents/verification/kra-pin/{verificationId}',    'document-verification', 'get-kra-pin-result'),
    ('post', '/api/v1/documents/verification/drivers-license',             'document-verification', 'verify-drivers-license'),
    ('get',  '/api/v1/documents/verification/drivers-license/{verificationId}', 'document-verification', 'get-drivers-license-result'),
    ('post', '/api/v1/documents/verification/vehicle-plate',               'document-verification', 'verify-vehicle-plate'),
    ('get',  '/api/v1/documents/verification/vehicle-plate/{verificationId}', 'document-verification', 'get-vehicle-plate-result'),

    # ── Voice Intelligence ───────────────────────────────────────────────────
    ('post', '/api/v1/voice-calls/initiate',               'voice-intelligence', 'initiate-call'),
    ('post', '/api/v1/voice-calls/{id}/end',               'voice-intelligence', 'end-call'),
    ('get',  '/api/v1/voice-calls/{id}',                   'voice-intelligence', 'get-call'),
    ('get',  '/api/v1/voice-calls',                        'voice-intelligence', 'list-calls'),
    ('get',  '/api/v1/voice-calls/{id}/recording',         'voice-intelligence', 'get-recording'),
    ('get',  '/api/v1/voice-calls/{id}/transcript',        'voice-intelligence', 'get-transcript'),
    ('post', '/api/v1/voice-calls/{id}/analyze',           'voice-intelligence', 'analyze-call'),
    ('post', '/api/v1/voice-calls/{id}/refresh-analysis',  'voice-intelligence', 'refresh-analysis'),
    ('get',  '/api/v1/voice-calls/{id}/vapi-status',       'voice-intelligence', 'call-status'),
    ('get',  '/api/v1/voice-calls/participant/{participantId}', 'voice-intelligence', 'calls-by-participant'),

    # ── Claims Management ────────────────────────────────────────────────────
    ('post',   '/api/v1/claims',               'claims', 'create'),
    ('get',    '/api/v1/claims',               'claims', 'list'),
    ('get',    '/api/v1/claims/{id}',          'claims', 'get'),
    ('patch',  '/api/v1/claims/{id}',          'claims', 'update'),
    ('patch',  '/api/v1/claims/{id}/status',   'claims', 'update-status'),
    ('post',   '/api/v1/claims/{id}/assign',   'claims', 'assign'),
    ('post',   '/api/v1/claims/{id}/pois',     'claims', 'add-participant'),
    ('get',    '/api/v1/claims/{id}/pois',     'claims', 'list-participants'),

    # ── Evidence Management ──────────────────────────────────────────────────
    ('post',  '/api/v1/evidence/public-upload/proxy-upload', 'evidence', 'upload'),
    ('get',   '/api/v1/evidence/claim/{claimId}',            'evidence', 'list-by-claim'),
    ('get',   '/api/v1/evidence/{id}',                       'evidence', 'get'),
    ('patch', '/api/v1/evidence/{id}/tags',                  'evidence', 'update-tags'),
    ('post',  '/api/v1/evidence/{id}/review',                'evidence', 'review'),

    # ── Participants ─────────────────────────────────────────────────────────
    ('post',   '/api/v1/participants',                       'participants', 'create'),
    ('get',    '/api/v1/participants',                       'participants', 'list'),
    ('get',    '/api/v1/participants/{id}',                  'participants', 'get'),
    ('patch',  '/api/v1/participants/{id}',                  'participants', 'update'),
    ('get',    '/api/v1/participants/{id}/detail',           'participants', 'detail'),
    ('post',   '/api/v1/participants/{id}/sanctions-check',  'participants', 'sanctions-check'),
    ('get',    '/api/v1/participants/{id}/sanctions-checks', 'participants', 'sanctions-checks'),
]

def resolve(schema):
    if not schema or '$ref' not in schema:
        return schema or {}
    parts = schema['$ref'].lstrip('#/').split('/')
    obj = SPEC
    for p in parts:
        obj = obj.get(p, {})
    return obj

def safe_desc(text, maxlen=200):
    if not text:
        return ''
    line = text.strip().split('\n')[0].strip()
    line = re.sub(r'\s+', ' ', line)
    line = line.replace('"', '\\"')
    return line[:maxlen]

def param_field(pin, name, schema, required, description=''):
    schema = resolve(schema)
    ptype = schema.get('type', 'string')
    if 'enum' in schema:
        vals = [str(v) for v in schema['enum'][:6]]
        ptype = ' | '.join(vals)  # no inner quotes — would break MDX JSX parsing
    req = ' required' if required else ''
    desc = description or schema.get('description', '')
    lines = [f'<ParamField {pin}="{name}" type="{ptype}"{req}>']
    if desc:
        lines.append(f'  {safe_desc(desc)}')
    lines.append('</ParamField>')
    return '\n'.join(lines)

nav = {}
created = 0
skipped = 0

for method, path, group, slug in ENDPOINTS:
    path_item = SPEC.get('paths', {}).get(path, {})
    op = path_item.get(method, {})
    if not op:
        print(f'  SKIP (not found): {method.upper()} {path}')
        skipped += 1
        continue

    title = op.get('summary', f'{method.upper()} {path}')
    title = title.replace('"', '\\"')
    desc = safe_desc(op.get('description', ''))

    lines = ['---', f'title: "{title}"', f'api: "{method.upper()} {path}"']
    if desc:
        lines.append(f'description: "{desc}"')
    lines.extend(['---', ''])

    for p in op.get('parameters', []):
        if p.get('in') in ('path', 'query', 'header'):
            lines.append(param_field(p['in'], p['name'], p.get('schema', {}),
                                     p.get('required', False), p.get('description', '')))
            lines.append('')

    rb = op.get('requestBody', {})
    if rb:
        content = rb.get('content', {})
        schema = None
        for ct in ('application/json', 'multipart/form-data'):
            if ct in content and 'schema' in content[ct]:
                schema = resolve(content[ct]['schema'])
                break
        if schema:
            required_props = schema.get('required', [])
            for prop_name, prop_schema in list(schema.get('properties', {}).items())[:12]:
                lines.append(param_field('body', prop_name, prop_schema,
                                         prop_name in required_props))
                lines.append('')

    out_dir = f'api-reference/{group}'
    os.makedirs(out_dir, exist_ok=True)
    out_file = f'{out_dir}/{slug}.mdx'
    with open(out_file, 'w') as f:
        f.write('\n'.join(lines))

    nav.setdefault(group, []).append(f'api-reference/{group}/{slug}')
    created += 1
    print(f'  ✅ {out_file}')

print(f'\nCreated {created}, skipped {skipped}')

GROUP_LABELS = {
    'authentication':         'Authentication',
    'kyc':                    'KYC Verification',
    'document-verification':  'Document Authenticity',
    'voice-intelligence':     'Voice Intelligence',
    'claims':                 'Claims Management',
    'evidence':               'Evidence Management',
    'participants':           'Participants & Sanctions',
}

print('\nNavigation JSON:\n')
groups_json = []
for grp, pages in nav.items():
    label = GROUP_LABELS.get(grp, grp.title())
    groups_json.append({'group': label, 'pages': pages})
print(json.dumps({'tab': 'API Reference', 'groups': groups_json}, indent=2))
