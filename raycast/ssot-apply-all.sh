#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title SSOT Apply All
# @raycast.mode fullOutput
# @raycast.packageName SSOT

# Optional parameters:
# @raycast.icon ⚡
# @raycast.needsConfirmation true

# Documentation:
# @raycast.description Aplicar todas as padronizações SSOT
# @raycast.author senal88
# @raycast.authorURL https://github.com/senal88

# Script
set -e

SSOT_CLI="${HOME}/Projects/1password-audit-expert/ops/bin/ssot"

if [[ -x "$SSOT_CLI" ]]; then
    echo "🚀 Aplicando todas as padronizações SSOT..."
    "$SSOT_CLI" apply-all
else
    echo "❌ SSOT CLI não encontrado"
    exit 1
fi
