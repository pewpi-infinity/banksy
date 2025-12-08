#!/usr/bin/env bash

LOCKFILE=".infinity_push_lock"

# If another push is happening, wait.
if [ -f "$LOCKFILE" ]; then
    echo "⏳ Infinity Gatekeeper: Push in progress. Waiting…"
    exit 0
fi

# Create lock
touch "$LOCKFILE"

# Add only tracked + new research files safely
git add -A

# If nothing changed, release lock and exit
if git diff --cached --quiet; then
    rm "$LOCKFILE"
    echo "✔ Nothing new to push."
    exit 0
fi

# Commit + push safely
git commit -m "∞ Infinity Sync $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# Remove lock
rm "$LOCKFILE"

echo "✔ Push completed safely."
