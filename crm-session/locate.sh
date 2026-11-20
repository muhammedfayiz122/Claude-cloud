# Sourced by stack.sh. Finds the two repositories a UI verification needs, from wherever the session
# is working: the directory itself, its parents, or their immediate children. A clone named
# frontend-c5, frontend4444 or crm-frontend is found the same way — by the name in its manifest.
# CRM_FRONTEND_DIR / CRM_BACKEND_DIR override the search.

_is_frontend() { grep -qs '"name": "crm-frontend"' "$1/package.json"; }
_is_backend() { grep -qs '^name = "crm-backend"' "$1/pyproject.toml"; }

_find_repo() { # $1 = _is_frontend | _is_backend
  local dir="$PWD" depth candidate
  for depth in 0 1 2 3; do
    if "$1" "$dir"; then echo "$dir"; return 0; fi
    for candidate in "$dir"/*/; do
      candidate="${candidate%/}"
      if "$1" "$candidate"; then echo "$candidate"; return 0; fi
    done
    dir="$(dirname "$dir")"
  done
  return 1
}

FRONTEND="${CRM_FRONTEND_DIR:-$(_find_repo _is_frontend || true)}"
BACKEND="${CRM_BACKEND_DIR:-$(_find_repo _is_backend || true)}"
if [ -z "$FRONTEND" ] || [ -z "$BACKEND" ]; then
  echo "verify-ui: could not find crm-frontend and crm-backend from $PWD." >&2
  echo "Run from the workspace that holds both clones, or set CRM_FRONTEND_DIR and CRM_BACKEND_DIR." >&2
  exit 2
fi
WORKSPACE="$(dirname "$FRONTEND")"
