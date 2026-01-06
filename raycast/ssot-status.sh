#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title SSOT Status
# @raycast.mode fullOutput
# @raycast.packageName SSOT

# Optional parameters:
# @raycast.icon 📊

# Documentation:
# @raycast.description Ver status SSOT completo
# @raycast.author senal88
# @raycast.authorURL https://github.com/senal88

# Script
set -e

SSOT_CLI="${HOME}/Projects/1password-audit-expert/ops/bin/ssot"

if [[ -x "$SSOT_CLI" ]]; then
    "$SSOT_CLI" status
else
    echo "❌ SSOT CLI não encontrado ou não executável"
    exit 1
fi
