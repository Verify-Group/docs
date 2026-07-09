#!/usr/bin/env bash
# update-openapi.sh — Download the partner-facing OpenAPI spec from the gateway
# and save it to api-reference/openapi.json for use by Mintlify.
#
# Usage:
#   ./scripts/update-openapi.sh                        # uses UAT (default)
#   ./scripts/update-openapi.sh production             # uses production gateway
#   ./scripts/update-openapi.sh https://custom.url/openapi.json
#
# Run this script whenever the API changes, then commit the updated spec.

set -euo pipefail

ENVIRONMENT="${1:-uat}"

case "$ENVIRONMENT" in
  prod|production)
    SPEC_URL="https://gateway.verify-group.io/api/swagger.json"
    ;;
  uat)
    SPEC_URL="https://uat.gateway.verify-group.io/api/swagger.json"
    ;;
  stage|staging)
    SPEC_URL="https://stage.gateway.verify-group.io/api/swagger.json"
    ;;
  http*|https*)
    SPEC_URL="$ENVIRONMENT"
    ;;
  *)
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [uat|production|staging|<url>]"
    exit 1
    ;;
esac

OUTPUT="api-reference/openapi.json"
mkdir -p api-reference

echo "⬇️  Downloading OpenAPI spec from $SPEC_URL ..."
curl --fail --silent --show-error --location "$SPEC_URL" -o "$OUTPUT"

# Quick sanity check
PATHS=$(python3 -c "import json,sys; d=json.load(open('$OUTPUT')); print(len(d.get('paths', {})))" 2>/dev/null || echo "unknown")
echo "✅  Saved to $OUTPUT  ($PATHS paths)"
echo ""
echo "Next steps:"
echo "  git add api-reference/openapi.json"
echo "  git commit -m 'chore(docs): update OpenAPI spec from $ENVIRONMENT'"
echo "  git push origin main"
