# Verify Group API Documentation

Partner-facing API documentation for the Verify Group Platform, built with [Mintlify](https://mintlify.com).

Published at: **https://docs.verify-group.com**

## What's documented

| Section | Description |
|---|---|
| **KYC Verification** | Individual standard/advanced, business, custom verification flows, and full history |
| **Document Authenticity** | National IDs, driver's licences, vehicle logbooks, KRA PINs, vehicle plates, custom document types |
| **Voice Intelligence** | Initiate calls, retrieve recordings & transcripts, trigger AI fraud analysis |
| **Claims Management** | Full insurance claim lifecycle — create, investigate, approve, settle |
| **Evidence Management** | Upload, tag, review, and attach supporting files to claims |
| **Participants & Sanctions** | Create participants, run watchlist checks, review sanctions results |

## Repository structure

```
docs/
├── docs.json                       # Mintlify configuration (theme, navigation, API server)
├── index.mdx                       # Introduction / landing page
├── quickstart.mdx                  # 5-minute getting started guide
├── authentication.mdx              # JWT auth and organisation headers
├── environments.mdx                # Environment URLs (prod, UAT, staging, local)
├── guides/                         # Step-by-step integration guides
├── api-reference/                  # Manual API pages (one MDX per endpoint)
│   ├── authentication/
│   ├── kyc/
│   ├── document-verification/
│   ├── voice-intelligence/
│   ├── claims/
│   ├── evidence/
│   └── participants/
├── webhooks/                       # Webhook events and security
├── sdks/                           # JavaScript SDK and Postman guides
├── changelog/                      # Release notes
├── logo/                           # Brand SVGs (light.svg + dark.svg)
└── scripts/
    ├── generate-manual-pages.py    # Regenerate MDX pages from openapi.json
    └── update-openapi.sh           # Download latest OpenAPI spec from gateway
```

## Local preview

```bash
pnpm add -g mintlify   # or: npm i -g mint
mint dev               # serves at http://localhost:3000
```

## Updating the OpenAPI spec

The `api-reference/openapi.json` snapshot is used for parameter extraction. Refresh it from the live gateway:

```bash
./scripts/update-openapi.sh             # pulls from UAT (default)
./scripts/update-openapi.sh production  # pulls from production
```

Then regenerate the MDX pages:

```bash
python3 scripts/generate-manual-pages.py
git add api-reference/ && git commit -m "chore(docs): refresh API pages from spec"
```

## Deployment

Merged to `main` → Mintlify auto-deploys to `docs.verify-group.com`.

**DNS (Cloudflare):**
```
docs.verify-group.com  CNAME  mint.mintlify.com
```

## API playground server

The interactive playground sends live requests to:

| Environment | URL |
|---|---|
| UAT (current default) | `https://uat.gateway.verify-group.io` |
| Production | `https://gateway.verify-group.io` |

To switch, update `api.mdx.server` in `docs.json`.

## Support

[tech@verify-group.com](mailto:tech@verify-group.com)
