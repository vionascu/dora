#!/bin/bash

echo "=========================================="
echo "DORA Dashboard Access Information"
echo "=========================================="
echo ""

# Get GitLab project info
GITLAB_REMOTE=$(git config --get remote.gitlab.url)
if [ -z "$GITLAB_REMOTE" ]; then
    echo "Error: No 'gitlab' remote found"
    exit 1
fi

# Extract project path from GitLab URL
# Format: https://git.ecd.axway.org/viionascu/dora.git
PROJECT_PATH=$(echo "$GITLAB_REMOTE" | sed 's|.*ecd.axway.org/||' | sed 's|\.git$||')
PROJECT_USER=$(echo "$PROJECT_PATH" | cut -d'/' -f1)
PROJECT_NAME=$(echo "$PROJECT_PATH" | cut -d'/' -f2)

echo "GitLab Project: $PROJECT_PATH"
echo ""

# Artifact preview URL (temporary - current run)
echo "Current Build Artifacts (temporary):"
echo "  https://viionascu.git-pages.ecd.axway.org/-/dora/-/jobs/8204432/artifacts/public/index.html"
echo ""

# Proper GitLab Pages URL (permanent after deployment)
echo "GitLab Pages URL (permanent after pages job completes):"
PAGES_URL="https://${PROJECT_USER}.git-pages.ecd.axway.org/${PROJECT_NAME}/public/"
echo "  $PAGES_URL"
echo ""

echo "Next Steps:"
echo "  1. Check pipeline: https://git.ecd.axway.org/viionascu/dora/-/pipelines"
echo "  2. Wait for 'pages' job to complete (green checkmark)"
echo "  3. Then access: $PAGES_URL"
echo ""
echo "Refresh the page after pages job completes to see the final dashboard."
echo ""

