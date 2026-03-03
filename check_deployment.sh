#!/bin/bash

echo "========================================================================"
echo "DORA GitLab Pages Deployment Diagnostics"
echo "========================================================================"
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "✗ Git is not installed"
    exit 1
fi

# Get project info
REMOTE_URL=$(git remote get-url origin)
PROJECT_NAME=$(basename "$REMOTE_URL" .git)
REMOTE_HOST=$(echo "$REMOTE_URL" | grep -oP '(?:https://|git@)[^/]+' | sed 's|https://||' | sed 's|git@||')

echo "Project Info:"
echo "  Remote: $REMOTE_URL"
echo "  Project: $PROJECT_NAME"
echo "  Host: $REMOTE_HOST"
echo ""

echo "Local Artifacts Check:"
echo "  public/:"
if [ -d "public" ]; then
    ls -la public/
    echo "  ✓ public/ directory exists"
    if [ -f "public/index.html" ]; then
        echo "  ✓ index.html found"
    fi
    if [ -d "public/calculations" ]; then
        echo "  ✓ calculations/ folder found"
    fi
else
    echo "  ✗ public/ directory not found"
fi
echo ""

echo "Local Git Status:"
git status --short
echo ""

echo "Next Steps:"
echo "  1. Push this commit to GitLab:"
echo "     git add . && git commit -m 'Fix: Remove emoji from CI config' && git push"
echo ""
echo "  2. Check pipeline status:"
echo "     https://git.ecd.axway.org/viionascu/dora/-/pipelines"
echo ""
echo "  3. Wait for 'pages' job to complete, then access:"
echo "     https://git.ecd.axway.org/viionascu/dora/-/pages/public/"
echo ""

