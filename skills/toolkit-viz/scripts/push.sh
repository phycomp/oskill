#!/bin/bash
# Deploy script — sync and push to Streamlit
set -e
REMOTE=$(git remote get-url origin 2>/dev/null || echo "no-remote")
echo "Remote: $REMOTE"
echo "Sync topics..."
python3 scripts/collect_topics.py
echo "Deploy complete"
