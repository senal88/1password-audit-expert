#!/usr/bin/env bash
# setup_1password_auditor.sh
# Setup automatizado 100% CLI para 1Password Security Auditor Expert
# Data: 2026-01-03
# Versão: v1.0

set -euo pipefail
export TZ="America/Sao_Paulo"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }

# Configurações
PROJECT_NAME="1password-audit-expert"
HF_SPACE="senal88/${PROJECT_NAME}"
LOCAL_DIR="${HOME}/Projects/${PROJECT_NAME}"
PROMPTS_DIR="${HOME}/Prompts"

print_banner() {
    echo "========================================"
    echo "🔐 1Password Security Auditor Expert"
    echo "   Setup Automatizado v1.0"
    echo "========================================"
    echo ""
}

check_dependencies() {
    log_info "Verificando dependências..."
    
    local missing=()
    
    # Git
    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    # Python
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi
    
    # 1Password CLI
    if ! command -v op &> /dev/null; then
        missing+=("op (1Password CLI)")
    fi
    
    # HuggingFace CLI
    if ! command -v huggingface-cli &> /dev/null; then
        log_warn "huggingface-cli não encontrado, instalando..."
        pip3 install -q huggingface_hub
    fi
    
    # Ollama (opcional)
    if ! command -v ollama &> /dev/null; then
        log_warn "Ollama não encontrado (opcional para uso local)"
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Dependências faltantes: ${missing[*]}"
        echo ""
        echo "Instale as dependências:"
        echo "  - Git: brew install git"
        echo "  - Python: brew install python"
        echo "  - 1Password CLI: brew install --cask 1password-cli"
        echo "  - Ollama: brew install ollama"
        exit 1
    fi
    
    log_success "Todas as dependências verificadas"
}

check_hf_auth() {
    log_info "Verificando autenticação HuggingFace..."
    
    if huggingface-cli whoami &> /dev/null; then
        local user
        user=$(huggingface-cli whoami 2>/dev/null | head -1)
        log_success "Autenticado como: ${user}"
        return 0
    fi
    
    log_warn "Não autenticado no HuggingFace"
    echo ""
    echo "Autenticando via SSH..."
    
    # Verificar SSH
    if ssh -T hf.co 2>&1 | grep -q "authenticated"; then
        log_success "SSH autenticado"
        return 0
    fi
    
    log_error "Falha na autenticação. Execute:"
    echo "  huggingface-cli login"
    echo "  # ou configure SSH: ssh-keygen -t ed25519"
    exit 1
}

check_op_auth() {
    log_info "Verificando autenticação 1Password CLI..."
    
    if op whoami --format json &> /dev/null; then
        local email
        email=$(op whoami --format json 2>/dev/null | jq -r '.email')
        log_success "1Password autenticado: ${email}"
        return 0
    fi
    
    log_warn "1Password CLI não autenticado"
    echo ""
    echo "Autenticando..."
    eval "$(op signin)"
    
    if op whoami &> /dev/null; then
        log_success "Autenticação bem-sucedida"
    else
        log_error "Falha na autenticação. Execute manualmente: eval \$(op signin)"
        exit 1
    fi
}

setup_local_project() {
    log_info "Configurando projeto local..."
    
    # Criar diretório
    mkdir -p "${LOCAL_DIR}"
    cd "${LOCAL_DIR}"
    
    # Criar estrutura
    mkdir -p cli gradio models scripts
    
    log_success "Estrutura criada em: ${LOCAL_DIR}"
}

install_python_deps() {
    log_info "Instalando dependências Python..."
    
    pip3 install -q ollama huggingface_hub gradio
    
    log_success "Dependências Python instaladas"
}

setup_ollama_model() {
    log_info "Configurando modelo Ollama..."
    
    if ! command -v ollama &> /dev/null; then
        log_warn "Ollama não instalado, pulando configuração do modelo"
        return 0
    fi
    
    # Verificar se modelo base existe
    if ! ollama list | grep -q "qwen2.5:14b"; then
        log_info "Baixando modelo base qwen2.5:14b..."
        ollama pull qwen2.5:14b
    fi
    
    # Criar Modelfile
    local modelfile="${LOCAL_DIR}/models/Modelfile.1password-auditor"
    
    if [[ -f "${modelfile}" ]]; then
        log_info "Criando modelo customizado..."
        ollama create 1password-auditor -f "${modelfile}"
        log_success "Modelo 1password-auditor criado"
    else
        log_warn "Modelfile não encontrado, usando modelo base"
    fi
}

create_hf_space() {
    log_info "Criando/atualizando HuggingFace Space..."
    
    local space_dir="${LOCAL_DIR}/gradio"
    
    # Verificar se Space existe
    if huggingface-cli repo info "${HF_SPACE}" --repo-type space &> /dev/null; then
        log_info "Space já existe, atualizando..."
    else
        log_info "Criando novo Space..."
        huggingface-cli repo create "${PROJECT_NAME}" --type space --sdk gradio
    fi
    
    # Clonar Space
    cd "${LOCAL_DIR}"
    if [[ -d "hf-space" ]]; then
        rm -rf hf-space
    fi
    
    git clone "git@hf.co:spaces/${HF_SPACE}" hf-space
    
    # Copiar arquivos
    cp -f gradio/app.py hf-space/
    cp -f gradio/requirements.txt hf-space/
    cp -f gradio/README.md hf-space/
    
    # Commit e push
    cd hf-space
    git add -A
    git commit -m "feat: Update 1Password Security Auditor Expert" || true
    git push
    
    log_success "Space atualizado: https://huggingface.co/spaces/${HF_SPACE}"
}

copy_to_prompts() {
    log_info "Copiando para diretório Prompts (SSOT)..."
    
    local target_dir="${PROMPTS_DIR}/05_Workflows"
    
    if [[ -d "${target_dir}" ]]; then
        # Encontrar próximo número
        local next_num
        next_num=$(ls -1 "${target_dir}" 2>/dev/null | grep -oE '^[0-9]{2}_' | sort -n | tail -1 | sed 's/_//')
        next_num=$((10#${next_num:-68} + 1))
        next_num=$(printf "%02d" "${next_num}")
        
        # Copiar CLI
        local cli_target="${target_dir}/${next_num}_audit_1password_expert_v1.0.py"
        cp "${LOCAL_DIR}/cli/audit_1password_expert.py" "${cli_target}"
        chmod +x "${cli_target}"
        
        log_success "CLI copiado para: ${cli_target}"
    else
        log_warn "Diretório Prompts não encontrado, pulando cópia"
    fi
}

print_usage() {
    echo ""
    echo "========================================"
    echo "✅ SETUP CONCLUÍDO!"
    echo "========================================"
    echo ""
    echo "📂 Projeto local: ${LOCAL_DIR}"
    echo "🌐 HuggingFace Space: https://huggingface.co/spaces/${HF_SPACE}"
    echo ""
    echo "📋 COMO USAR:"
    echo ""
    echo "1. Via CLI local (recomendado para privacidade):"
    echo "   cd ${LOCAL_DIR}/cli"
    echo "   python3 audit_1password_expert.py --vaults 1p_vps"
    echo ""
    echo "2. Via HuggingFace Space (interface web):"
    echo "   Acesse: https://huggingface.co/spaces/${HF_SPACE}"
    echo ""
    echo "3. Comandos úteis:"
    echo "   # Exportar cofre"
    echo "   op item list --vault 1p_vps --format json > export.json"
    echo ""
    echo "   # Auditoria rápida"
    echo "   python3 audit_1password_expert.py --vaults 1p_vps --hf"
    echo ""
    echo "   # Apenas exportar (sem análise)"
    echo "   python3 audit_1password_expert.py --vaults 1p_vps --export-only"
    echo ""
    echo "========================================"
}

main() {
    print_banner
    
    # Parse args
    local skip_hf=false
    local skip_ollama=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-hf) skip_hf=true; shift ;;
            --skip-ollama) skip_ollama=true; shift ;;
            --help) 
                echo "Uso: $0 [--skip-hf] [--skip-ollama]"
                exit 0 
                ;;
            *) shift ;;
        esac
    done
    
    # Executar setup
    check_dependencies
    check_op_auth
    
    if [[ "${skip_hf}" != true ]]; then
        check_hf_auth
    fi
    
    setup_local_project
    install_python_deps
    
    if [[ "${skip_ollama}" != true ]]; then
        setup_ollama_model
    fi
    
    if [[ "${skip_hf}" != true ]]; then
        create_hf_space
    fi
    
    copy_to_prompts
    print_usage
}

# Executar
main "$@"
