#!/bin/bash
# Runs the backup-restore verifier up to (and past) the schema apply; reports whether db/schema.sql applies on an empty DB.
d=$1; cd $d || exit 2
out=$(timeout 600 bash deploy/scripts/verify_backup_restore.sh 2>&1)
if echo "$out" | grep -q "reads and writes every seeded tenant before the backup"; then echo "$d: schema applies OK"; else echo "$d: FAILED"; echo "$out" | grep -E "ERROR|error" | head -5; fi
docker ps -a --format '{{.Names}}' | grep -E "crm-verify|backup" | xargs -r docker rm -f >/dev/null 2>&1
