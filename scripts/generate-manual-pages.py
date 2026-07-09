#!/usr/bin/env python3
"""
Generate Mintlify manual API pages from openapi.json.
Each selected endpoint becomes an MDX file with proper frontmatter.
"""
import json, os, re

SPEC = json.load(open('api-reference/openapi.json'))

# (method, path, group-dir, slug)
ENDPOINTS = [
    # Authentication
    ('post',   '/api/v1/auth/login',                                            'authentication', 'login'),
    ('post',   '/api/v1/auth/logout',                                           'authentication', 'logout'),
    ('post',   '/api/v1/auth/refresh',                                          'authentication', 'refresh'),
    ('get',    '/api/v1/auth/me',                                               'authentication', 'me'),
    # MFA
    ('get',    '/api/v1/mfa/status',                                            'mfa', 'status'),
    ('post',   '/api/v1/mfa/enable',                                            'mfa', 'enable'),
    ('post',   '/api/v1/mfa/verify',                                            'mfa', 'verify'),
    ('delete', '/api/v1/mfa',                                                   'mfa', 'disable'),
    # Users
    ('get',    '/api/v1/users/me',                                              'users', 'me'),
    ('put',    '/api/v1/users/{id}',                                            'users', 'update'),
    ('post',   '/api/v1/users/me/change-password',                              'users', 'change-password'),
    ('get',    '/api/v1/users/me/notification-preferences',                     'users', 'notification-preferences'),
    ('put',    '/api/v1/users/me/notification-preferences',                     'users', 'update-notifications'),
    ('post',   '/api/v1/users/me/avatar',                                       'users', 'upload-avatar'),
    # Organizations
    ('get',    '/api/v1/organizations/{id}',                                    'organizations', 'get'),
    ('put',    '/api/v1/organizations/{id}',                                    'organizations', 'update'),
    ('get',    '/api/v1/organizations/{id}/members',                            'organizations', 'list-members'),
    ('get',    '/api/v1/organizations/{id}/dashboard',                          'organizations', 'dashboard'),
    ('get',    '/api/v1/organizations/{id}/token-balance',                      'organizations', 'token-balance'),
    ('post',   '/api/v1/organizations/{id}/run-kyc',                           'organizations', 'run-kyc'),
    # Participants
    ('post',   '/api/v1/participants',                                          'participants', 'create'),
    ('get',    '/api/v1/participants',                                          'participants', 'list'),
    ('get',    '/api/v1/participants/{id}',                                     'participants', 'get'),
    ('get',    '/api/v1/participants/{id}/detail',                              'participants', 'detail'),
    ('patch',  '/api/v1/participants/{id}',                                     'participants', 'update'),
    ('delete', '/api/v1/participants/{id}',                                     'participants', 'delete'),
    ('get',    '/api/v1/participants/sanctions-sources',                        'participants', 'sanctions-sources'),
    ('post',   '/api/v1/participants/{id}/sanctions-check',                    'participants', 'sanctions-check'),
    ('get',    '/api/v1/participants/{id}/sanctions-checks',                   'participants', 'sanctions-checks'),
    # Claims
    ('post',   '/api/v1/claims',                                                'claims', 'create'),
    ('get',    '/api/v1/claims',                                                'claims', 'list'),
    ('get',    '/api/v1/claims/{id}',                                           'claims', 'get'),
    ('patch',  '/api/v1/claims/{id}',                                           'claims', 'update'),
    ('delete', '/api/v1/claims/{id}',                                           'claims', 'delete'),
    ('patch',  '/api/v1/claims/{id}/status',                                   'claims', 'update-status'),
    ('post',   '/api/v1/claims/{id}/assign',                                   'claims', 'assign'),
    ('post',   '/api/v1/claims/{id}/pois',                                     'claims', 'add-poi'),
    ('get',    '/api/v1/claims/{id}/pois',                                     'claims', 'list-pois'),
    # Voice Interview
    ('post',   '/api/v1/claims/voice-interview/{claimId}/initiate',            'voice-interview', 'initiate'),
    ('patch',  '/api/v1/claims/voice-interview/sessions/{sessionId}/audio',    'voice-interview', 'upload-audio'),
    ('get',    '/api/v1/claims/voice-interview/{claimId}/sessions',            'voice-interview', 'list-sessions'),
    ('get',    '/api/v1/claims/voice-interview/sessions/{sessionId}/results',  'voice-interview', 'results'),
    # Evidence
    ('post',   '/api/v1/evidence/upload',                                      'evidence', 'upload'),
    ('get',    '/api/v1/evidence/claim/{claimId}',                             'evidence', 'list-by-claim'),
    ('get',    '/api/v1/evidence/{id}',                                        'evidence', 'get'),
    ('delete', '/api/v1/evidence/{id}',                                        'evidence', 'delete'),
    ('patch',  '/api/v1/evidence/{id}/tags',                                   'evidence', 'update-tags'),
    ('post',   '/api/v1/evidence/{id}/review',                                 'evidence', 'review'),
    # Tokens
    ('get',    '/api/v1/tokens/me/balance',                                    'tokens', 'my-balance'),
    ('get',    '/api/v1/tokens/me/transactions',                               'tokens', 'my-transactions'),
    ('post',   '/api/v1/tokens/purchase',                                      'tokens', 'purchase'),
    ('post',   '/api/v1/tokens/consume',                                       'tokens', 'consume'),
    ('get',    '/api/v1/tokens/balance/{ownerId}',                             'tokens', 'balance'),
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
        ptype = ' | '.join(f'"{v}"' for v in vals)
    req = ' required' if required else ''
    desc = description or schema.get('description', '')
    lines = [f'<ParamField {pin}="{name}" type="{ptype}"{req}>']
    if desc:
        lines.append(f'  {safe_desc(desc)}')
    lines.append('</ParamField>')
    return '\n'.join(lines)

nav = {}  # group -> [page_path]
created = 0

for method, path, group, slug in ENDPOINTS:
    path_item = SPEC.get('paths', {}).get(path, {})
    op = path_item.get(method, {})
    if not op:
        print(f'  SKIP (not found): {method.upper()} {path}')
        continue

    title = op.get('summary', f'{method.upper()} {path}')
    title = title.replace('"', '\\"')
    desc = safe_desc(op.get('description', ''))

    lines = ['---', f'title: "{title}"', f'api: "{method.upper()} {path}"']
    if desc:
        lines.append(f'description: "{desc}"')
    lines.extend(['---', ''])

    # Path + query params
    for p in op.get('parameters', []):
        if p.get('in') in ('path', 'query', 'header'):
            lines.append(param_field(
                p['in'], p['name'],
                p.get('schema', {}),
                p.get('required', False),
                p.get('description', '')
            ))
            lines.append('')

    # Request body (top-level properties, max 12)
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
                lines.append(param_field(
                    'body', prop_name,
                    prop_schema,
                    prop_name in required_props
                ))
                lines.append('')

    out_dir = f'api-reference/{group}'
    os.makedirs(out_dir, exist_ok=True)
    out_file = f'{out_dir}/{slug}.mdx'
    with open(out_file, 'w') as f:
        f.write('\n'.join(lines))

    page_ref = f'api-reference/{group}/{slug}'
    nav.setdefault(group, []).append(page_ref)
    created += 1
    print(f'  ✅ {out_file}')

print(f'\nCreated {created} pages.\n')
print('Navigation snippet for docs.json:\n')

groups_json = []
GROUP_LABELS = {
    'authentication': 'Authentication',
    'mfa': 'Multi-Factor Authentication',
    'users': 'Users',
    'organizations': 'Organizations',
    'participants': 'Participants',
    'claims': 'Claims',
    'voice-interview': 'Voice Interview',
    'evidence': 'Evidence',
    'tokens': 'Tokens',
}
for grp, pages in nav.items():
    label = GROUP_LABELS.get(grp, grp.title())
    groups_json.append({'group': label, 'pages': pages})

print(json.dumps({'tab': 'API Reference', 'groups': groups_json}, indent=2))
