#!/bin/bash
# .devcontainer/post-create.sh
# Setup script executado após criação do container

set -e

echo "🚀 Iniciando setup do DevContainer..."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }

# 1. Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip

# 2. Instalar dependências Python
log_info "Instalando dependências Python..."
pip install -r cli/requirements.txt
pip install -r gradio/requirements.txt

# Instalar ferramentas de desenvolvimento
pip install black ruff pytest pytest-cov ipython

log_success "Dependências Python instaladas"

# 3. Instalar 1Password CLI (se não estiver instalado)
if ! command -v op &> /dev/null; then
    log_info "Instalando 1Password CLI..."

    # Detectar arquitetura
    ARCH=$(dpkg --print-architecture)

    # Download e instalação
    curl -sS https://downloads.1password.com/linux/tar/stable/x86_64/1password-cli-latest.tar.gz | \
        tar -xz -C /tmp

    sudo mv /tmp/op /usr/local/bin/
    sudo chmod +x /usr/local/bin/op

    log_success "1Password CLI instalado"
else
    log_success "1Password CLI já instalado"
fi

# 4. Configurar Git
log_info "Configurando Git..."
git config --global core.editor "code --wait"
git config --global init.defaultBranch main
git config --global pull.rebase false

log_success "Git configurado"

# 5. Criar diretórios de trabalho
log_info "Criando diretórios de trabalho..."
mkdir -p ops/state ops/policy ops/templates

log_success "Diretórios criados"

# 6. Verificar GitHub CLI
if command -v gh &> /dev/null; then
    log_info "GitHub CLI disponível"

    # Verificar autenticação (se possível)
    if gh auth status &> /dev/null; then
        log_success "GitHub CLI autenticado"
    else
        echo "⚠️  GitHub CLI não autenticado. Execute: gh auth login"
    fi
fi

# 7. Criar aliases úteis
log_info "Configurando aliases..."
cat >> ~/.bashrc << 'EOF'

# Aliases 1Password Audit Expert
alias audit='python /workspaces/1password-audit-expert/cli/audit_1password_expert.py'
alias ssot='/workspaces/1password-audit-expert/ops/bin/ssot'
alias gradio-dev='cd /workspaces/1password-audit-expert/gradio && python app.py'

# Aliases Git
alias gs='git status'
alias gp='git pull'
alias gc='git commit -m'
alias glog='git log --oneline --graph --all -10'

# Aliases úteis
alias ll='ls -lah'
alias ..='cd ..'

EOF

log_success "Aliases configurados"

# 8. Exibir informações do ambiente
echo ""
echo "=========================================="
echo "  ✅ DevContainer Setup Completo!"
echo "=========================================="
echo ""
echo "📦 Ferramentas instaladas:"
echo "  - Python $(python --version 2>&1 | cut -d' ' -f2)"
echo "  - pip $(pip --version | cut -d' ' -f2)"
echo "  - Node.js $(node --version)"
echo "  - GitHub CLI $(gh --version | head -1)"
echo "  - 1Password CLI $(op --version)"
echo ""
echo "🔧 Comandos disponíveis:"
echo "  audit --help          # CLI de auditoria"
echo "  ssot status           # Status SSOT"
echo "  gradio-dev            # Iniciar Gradio"
echo "  gh auth login         # Autenticar GitHub"
echo ""
echo "📖 Documentação:"
echo "  cat README.md"
echo "  cat SETUP_COMPLETE.md"
echo ""
echo "🚀 Próximo passo:"
echo "  1. Configure secrets via GitHub Codespaces UI"
echo "  2. Execute: audit --vaults 1p_vps"
echo ""

# 9. Verificar secrets (avisar se não estiverem configurados)
if [[ -z "${SHARED_OPENAI_API_KEY:-}" ]]; then
    echo "⚠️  AVISO: Secrets não configurados!"
    echo ""
    echo "Configure via GitHub Codespaces:"
    echo "  1. Abra configurações do Codespace"
    echo "  2. Adicione secrets de usuário:"
    echo "     - SHARED_OPENAI_API_KEY"
    echo "     - SHARED_HUGGINGFACE_TOKEN"
    echo "     - SHARED_PERPLEXITY_API_KEY"
    echo ""
    echo "Ou via CLI:"
    echo "  gh secret set SHARED_OPENAI_API_KEY --app codespaces --user"
    echo ""
fi

log_success "Setup concluído!"
