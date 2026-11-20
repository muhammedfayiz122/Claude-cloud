#!/usr/bin/env bash
# The local stack a UI verification runs against. See ../SKILL.md.
#
#   stack.sh db [name]   fresh database: create, migrate, login roles, dev tenant, baseline, bucket
#   stack.sh api         crm-backend on 127.0.0.1:8000 (foreground — run it in the background)
#   stack.sh web         crm-frontend on localhost:5199, proxying /api to :8000 (foreground)
#   stack.sh status      what is up
#   stack.sh stop        stop whatever listens on :8000 and :5199
set -euo pipefail

SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=locate.sh
. "$SCRIPTS/locate.sh"
DB="${DB:-${2:-crm_verify}}"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5199}"
export PATH="/home/user/tools/node24/node_modules/.bin:$PATH"
ORG_ID="${CRM_DEV_ORGANIZATION_ID:-7b0c6a58-5c1e-4f5a-9f0a-2d1f3c4b5a61}"
PRINCIPAL="${CRM_DEV_PRINCIPAL_ID:-local-verifier}"
COMPOSE=(docker compose -f "$BACKEND/docker-compose.test.yml")

backend_env() {
  export CRM_DATABASE_URL="postgresql+asyncpg://crm_app_login:crm_app_login@127.0.0.1:15432/$DB"
  export CRM_DISPATCHER_DATABASE_URL="postgresql+asyncpg://crm_dispatcher_login:crm_dispatcher_login@127.0.0.1:15432/$DB"
  export CRM_RUNTIME_DATABASE_URL="postgresql+asyncpg://crm_runtime_login:crm_runtime_login@127.0.0.1:15432/$DB"
  export CRM_MIGRATION_DATABASE_URL="postgresql+asyncpg://crm_superuser:crm_superuser@127.0.0.1:15432/$DB"
  export CRM_S3_BUCKET=crm-dev CRM_S3_REGION=us-east-1 CRM_S3_ENDPOINT_URL=http://127.0.0.1:19000
  export CRM_S3_ACCESS_KEY_ID=crmtestaccess CRM_S3_SECRET_ACCESS_KEY=crmtestsecret
  export CRM_S3_ADDRESSING_STYLE=path CRM_S3_SERVER_SIDE_ENCRYPTION=aws:kms CRM_S3_SSE_KEY_ID=crm-test-key
  export CRM_RENDERER_URL=http://127.0.0.1:13000 CRM_RENDERER_ENGINE=gotenberg/gotenberg:8.38.1-chromium
  export CRM_CLAMAV_HOST=127.0.0.1 CRM_CLAMAV_PORT=13310
  export CRM_ENVIRONMENT=development CRM_DEV_PRINCIPAL_ID="$PRINCIPAL" CRM_DEV_ORGANIZATION_ID="$ORG_ID"
  # Every capability key the backend declares, read from the code so it cannot go stale.
  CRM_DEV_ENTITLEMENTS="$(grep -rhoE '^[A-Z_]*KEY: Final = "crm\.[a-z_]+"' "$BACKEND"/src/crm/capabilities/*/capability.py \
    | sed -E 's/.*"(crm\.[a-z_]+)"/\1/' | sort -u | paste -sd, -)"
  export CRM_DEV_ENTITLEMENTS
}

psql_super() { "${COMPOSE[@]}" exec -T postgres psql -U crm_superuser -d "$DB" -v ON_ERROR_STOP=1 -q "$@"; }

case "${1:-}" in
  db)
    backend_env
    cd "$BACKEND"
    if "${COMPOSE[@]}" exec -T postgres psql -U crm_superuser -d postgres -tAc \
      "SELECT 1 FROM pg_database WHERE datname = '$DB'" | grep -q 1; then
      echo "== $DB exists; migrating it forward (DB=<new name> for a clean tenant)"
    else
      "${COMPOSE[@]}" exec -T postgres createdb -U crm_superuser "$DB"
    fi
    uv run alembic upgrade head 2>&1 | tail -1
    psql_super -v app_password=crm_app_login -v dispatcher_password=crm_dispatcher_login \
      -v maintenance_password=crm_maintenance_login -v migrate_password=crm_migrate_login \
      -v provision_password=crm_provision_login -v runtime_password=crm_runtime_login < deploy/sql/bootstrap_roles.sql 2>&1 | grep -v NOTICE | tail -1
    uv run python tools/dev_seed.py | psql_super 2>&1 | tail -1
    uv run python tools/dev_baseline.py 2>&1 | grep -v '"level"' | tail -2
    # Durable runtime schema (dbos) so the automation worker can start.
    psql_super < deploy/sql/migration_privileges.sql 2>&1 | grep -v NOTICE | tail -1 || true
    psql_super -v runtime_password=crm_runtime_login < deploy/sql/runtime_login.sql 2>&1 | grep -v NOTICE | tail -1 || true
    CRM_MIGRATION_DATABASE_URL="postgresql+asyncpg://crm_migrate_login:crm_migrate_login@127.0.0.1:15432/$DB" uv run python -m crm runtime-migrate 2>&1 | grep -v '"level"' | tail -1
    # Verification databases only: a configuring tenant draws onboarding over every route.
    psql_super -c "UPDATE organizations SET readiness_state = 'crm_ready' WHERE id = '$ORG_ID'"
    curl -s -X PUT http://127.0.0.1:19000/crm-dev -o /dev/null || true
    echo "== $DB ready for organization $ORG_ID, principal $PRINCIPAL"
    ;;
  api)
    backend_env
    cd "$BACKEND"
    exec uv run uvicorn crm.main:app --host 127.0.0.1 --port "$API_PORT"
    ;;
  worker)
    backend_env
    cd "$BACKEND"
    export CRM_RUNTIME_TARGET_VERSION="$(cd "$BACKEND" && uv run python -c "from crm.durable.compat import COMPAT_VERSION as v; print(v)" 2>/dev/null)"
    export CRM_WORKER_EXECUTOR_ID="local-$DB-worker"
    export CRM_WORKER_METRICS_PORT="${WORKER_METRICS_PORT:-$((API_PORT+1000))}"
    exec uv run python -m crm automation-worker
    ;;
  web)
    cd "$FRONTEND"
    CRM_DEV_API_ORIGIN=http://127.0.0.1:$API_PORT VITE_DEV_ACCESS_TOKEN="$PRINCIPAL" exec pnpm dev --port "$WEB_PORT"
    ;;
  status)
    printf 'api    %s\n' "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:$API_PORT/health/ready || true)"
    printf 'web    %s\n' "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$WEB_PORT/ || true)"
    printf 'proxy  %s\n' "$(curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer x' http://localhost:$WEB_PORT/api/v1/session || true)"
    ;;
  stop)
    fuser -k "$API_PORT/tcp" "$WEB_PORT/tcp" 2>/dev/null; echo stopped
    ;;
  *)
    sed -n '2,9p' "$0"
    exit 2
    ;;
esac
