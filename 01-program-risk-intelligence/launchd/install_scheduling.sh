#!/bin/bash
# Installs and activates the three weekly_cycle.py phases as launchd user
# agents: first-request (Wed 9am), followup (Fri 8am), report (Fri 3pm).
#
# From this point on, these run unattended -- no confirmation, no chat
# session needed. first-request drafts real emails; followup checks who's
# replied and drafts follow-ups only to non-responders; report classifies,
# detects patterns, generates both report altitudes, and posts comments to
# real Jira tickets. Run this only when you're ready for that.
set -e

PLIST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/Library/LaunchAgents"
mkdir -p "$DEST"

for plist in "$PLIST_DIR"/com.programriskintelligence.*.plist; do
    name=$(basename "$plist")
    label="${name%.plist}"
    cp "$plist" "$DEST/$name"
    launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$DEST/$name"
    echo "Installed and activated: $label"
done

echo ""
echo "Done. Logs will appear in ../logs/*.log as jobs run."
echo "Check status any time with: launchctl list | grep programriskintelligence"
echo "To stop everything: ./uninstall_scheduling.sh"
