#!/bin/bash

echo "========================================================================"
echo "GitLab Pipeline Diagnostics"
echo "========================================================================"
echo ""

GITLAB_PROJECT_URL="https://git.ecd.axway.org/api/v4/projects/viionascu%2Fdora"
GITLAB_TOKEN="${GITLAB_TOKEN}"

if [ -z "$GITLAB_TOKEN" ]; then
    echo "⚠️  GITLAB_TOKEN not set in environment"
    echo ""
    echo "To check pipeline status, visit:"
    echo "  https://git.ecd.axway.org/viionascu/dora/-/pipelines"
    echo ""
    echo "Look for:"
    echo "  ✓ collect_git - Should be completed"
    echo "  ✓ calculate_metrics - Should be completed"
    echo "  ⏳ pages - Should be in progress or completed"
    echo ""
    echo "Once 'pages' job shows a green checkmark, the dashboard will be available at:"
    echo "  https://viionascu.git-pages.ecd.axway.org/dora/public/"
    echo ""
    exit 0
fi

echo "Fetching latest pipeline..."
PIPELINES=$(curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_PROJECT_URL/pipelines?per_page=1")
LATEST_PIPELINE_ID=$(echo "$PIPELINES" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

if [ -z "$LATEST_PIPELINE_ID" ]; then
    echo "✗ Could not fetch pipeline information"
    exit 1
fi

echo "Latest Pipeline ID: $LATEST_PIPELINE_ID"
echo ""

JOBS=$(curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_PROJECT_URL/pipelines/$LATEST_PIPELINE_ID/jobs")

echo "Job Status:"
echo "$JOBS" | grep -o '"name":"[^"]*".*"status":"[^"]*"' | sed 's/"name":"/  /g' | sed 's/".*"status":"/: /g' | sed 's/"//g'

echo ""
echo "Dashboard URL:"
echo "  https://viionascu.git-pages.ecd.axway.org/dora/public/"

