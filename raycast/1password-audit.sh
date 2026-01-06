#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title 1Password Audit
# @raycast.mode fullOutput
# @raycast.packageName 1Password Security

# Optional parameters:
# @raycast.icon 🔐
# @raycast.argument1 { "type": "text", "placeholder": "Vault (ex: 1p_vps)", "optional": true }
# @raycast.argument2 { "type": "dropdown", "placeholder": "Backend", "data": [{"title": "Ollama (Local)", "value": "ollama"}, {"title": "HuggingFace API", "value": "hf"}], "optional": true }

# Documentation:
# @raycast.description Execute auditoria de segurança em cofres 1Password
# @raycast.author senal88
# @raycast.authorURL https://github.com/senal88

# Script
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLI_SCRIPT="${HOME}/Projects/1password-audit-expert/cli/audit_1password_expert.py"

# Verificar se CLI existe
if [[ ! -f "$CLI_SCRIPT" ]]; then
    echo "❌ CLI não encontrado em: $CLI_SCRIPT"
    exit 1
fi

# Verificar autenticação 1Password
if ! op whoami &> /dev/null; then
    echo "❌ 1Password CLI não autenticado"
    echo "Execute: eval \$(op signin)"
    exit 1
fi

# Executar auditoria
vault="${1:-}"
backend="${2:-ollama}"

if [[ -n "$vault" ]]; then
    if [[ "$backend" == "hf" ]]; then
        echo "🚀 Executando auditoria de '${vault}' via HuggingFace..."
        python3 "$CLI_SCRIPT" --vaults "$vault" --hf
    else
        echo "🚀 Executando auditoria de '${vault}' via Ollama..."
        python3 "$CLI_SCRIPT" --vaults "$vault"
    fi
else
    echo "🚀 Executando auditoria interativa..."
    python3 "$CLI_SCRIPT"
fi
