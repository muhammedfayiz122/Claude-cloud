#!/usr/bin/env bash
# repin.sh <frontend_dir> <backend_dir>: copy the backend's openapi into the frontend contract copy,
# write crm-openapi.source.json (ref = backend HEAD) and update the DOCUMENT_INDEX row.
set -euo pipefail
FE="$1"; BE="$2"
cd "$FE"
git checkout --theirs docs/DOCUMENT_INDEX.md docs/engineering/crm-openapi.source.json 2>/dev/null || true
H=$(git -C "$BE" rev-parse HEAD)
cp "$BE/openapi/crm-openapi.yaml" docs/engineering/crm-openapi.yaml
B=$(stat -c %s docs/engineering/crm-openapi.yaml); S=$(sha256sum docs/engineering/crm-openapi.yaml | cut -d' ' -f1)
printf '{\n  "repository": "code7/business-ecosystem/crm/crm-backend",\n  "ref": "%s",\n  "path": "openapi/crm-openapi.yaml",\n  "bytes": %s,\n  "sha256": "%s"\n}\n' "$H" "$B" "$S" > docs/engineering/crm-openapi.source.json
python3 - "$B" "${S:0:16}" <<'PY'
import re,sys
p='docs/DOCUMENT_INDEX.md'; t=open(p).read()
t=re.sub(r'<<<<<<< [^\n]*\n.*?>>>>>>> [^\n]*\n', lambda m: m.group(0).split('=======\n')[1].rsplit('>>>>>>>',1)[0], t, flags=re.S)
t=re.sub(r"\| `engineering` \| `crm-openapi.yaml` — read-only copy; the backend owns it \| 1.0.0-slice1 \| [0-9,]+ \| `[0-9a-f]+` \|", "| `engineering` | `crm-openapi.yaml` — read-only copy; the backend owns it | 1.0.0-slice1 | %s | `%s` |" % (f"{int(sys.argv[1]):,}", sys.argv[2]), t)
open(p,'w').write(t)
PY
echo "re-pinned to $H ($B bytes, ${S:0:16})"
