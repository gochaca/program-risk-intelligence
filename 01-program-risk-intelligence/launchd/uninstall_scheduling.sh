#!/bin/bash
# Stops and removes all three scheduled weekly_cycle.py jobs.
DEST="$HOME/Library/LaunchAgents"

for label in \
    com.programriskintelligence.first-request \
    com.programriskintelligence.followup \
    com.programriskintelligence.report
do
    launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
    rm -f "$DEST/$label.plist"
    echo "Removed: $label"
done

echo ""
echo "All scheduled jobs stopped and removed."
