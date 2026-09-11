#!/bin/bash

# Read the JSON tool payload from stdin
PAYLOAD=$(cat)

# Check if the command targets the macOS /tmp/ directory or files ending in .tmp
if echo "$PAYLOAD" | grep -iE -q "/tmp/|\.tmp$|temp_"; then
    # It looks like a temporary file. Bypass permissions and auto-allow.
    echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
else
    # It is a standard file deletion. Fall back to prompting the user.
    echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask"}}'
fi

# Exit 0 ensures Claude Code processes the JSON response
exit 0