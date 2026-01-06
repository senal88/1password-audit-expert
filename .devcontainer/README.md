# DevContainer & Codespaces - Guia Completo

## 🎯 O que é DevContainer?

DevContainer permite executar todo o ambiente de desenvolvimento dentro de um container Docker, garantindo:
- ✅ Ambiente idêntico para todos os desenvolvedores
- ✅ Configuração automática de ferramentas
- ✅ Secrets gerenciados via GitHub Codespaces
- ✅ Zero configuração local necessária

## 🚀 Como Usar

### Opção 1: GitHub Codespaces (Recomendado)

#### 1.1. Criar Codespace
```bash
# Via GitHub UI:
# 1. Vá para https://github.com/senal88/1password-audit-expert
# 2. Clique em "Code" > "Codespaces" > "Create codespace on main"

# Ou via CLI:
gh codespace create -r senal88/1password-audit-expert
```

#### 1.2. Configurar Secrets (ANTES de usar)

**Via GitHub UI:**
1. Acesse https://github.com/settings/codespaces
2. Clique em "New secret"
3. Adicione os seguintes secrets:

| Nome | Valor | Fonte |
|------|-------|-------|
| `SHARED_OPENAI_API_KEY` | `sk-...` | 1Password: `op://vault/OPENAI/api_key` |
| `SHARED_HUGGINGFACE_TOKEN` | `hf_...` | 1Password: `op://vault/HUGGINGFACE/api_key` |
| `SHARED_PERPLEXITY_API_KEY` | `pplx-...` | 1Password: `op://vault/PERPLEXITY/api_key` |
| `SHARED_GITHUB_TOKEN` | `ghp_...` | 1Password: `op://vault/GITHUB/api_token` |

**Via CLI (local macOS):**
```bash
# Autenticar 1Password
eval $(op signin)

# Sincronizar secrets para Codespaces
cd ~/DevOps/1password-audit-expert
ops/bin/ssot sync-gh-codespaces

# Verificar
gh secret list --app codespaces --user
```

#### 1.3. Abrir no VS Code
```bash
# Listar codespaces
gh codespace list

# Conectar
gh codespace code -c <nome-do-codespace>
```

### Opção 2: DevContainer Local (VS Code)

#### 2.1. Pré-requisitos
- VS Code instalado
- Extensão "Dev Containers" instalada
- Docker Desktop rodando

#### 2.2. Abrir DevContainer
```bash
# 1. Abrir projeto no VS Code
code ~/DevOps/1password-audit-expert

# 2. VS Code vai detectar .devcontainer/
# 3. Clique em "Reopen in Container"

# Ou via Command Palette (Cmd+Shift+P):
# > Dev Containers: Reopen in Container
```

#### 2.3. Configurar Secrets (local)
```bash
# No seu macOS (fora do container):
eval $(op signin)

# Exportar secrets para o shell
export SHARED_OPENAI_API_KEY=$(op read "op://vault/OPENAI/api_key")
export SHARED_HUGGINGFACE_TOKEN=$(op read "op://vault/HUGGINGFACE/api_key")

# Reabrir container (secrets serão injetados via remoteEnv)
```

## 🔧 O que é Instalado Automaticamente

### Ferramentas Base
- ✅ Python 3.11
- ✅ Node.js 20
- ✅ Git
- ✅ Zsh (shell padrão)

### CLI Tools
- ✅ 1Password CLI (`op`)
- ✅ GitHub CLI (`gh`)

### Python Packages
- ✅ ollama, huggingface_hub, gradio (produção)
- ✅ black, ruff, pytest (desenvolvimento)

### VS Code Extensions
- ✅ Python + Pylance
- ✅ GitHub Copilot
- ✅ GitLens
- ✅ Docker
- ✅ YAML, Prettier

### Aliases Úteis
```bash
audit --help          # CLI de auditoria 1Password
ssot status           # Status SSOT
gradio-dev            # Iniciar interface Gradio
gs                    # git status
gc "msg"              # git commit -m "msg"
ll                    # ls -lah
```

## 📊 Portas Expostas

| Porta | Serviço | Auto-forward |
|-------|---------|--------------|
| 7860 | Gradio Interface | Sim (com notificação) |
| 8000 | API Server | Sim (silencioso) |

## 🔒 Secrets e Segurança

### Como Funcionam os Secrets

1. **GitHub Codespaces:**
   - Secrets definidos em https://github.com/settings/codespaces
   - Injetados automaticamente como variáveis de ambiente
   - Acessíveis via `${localEnv:SHARED_*}`

2. **DevContainer Local:**
   - Usa variáveis de ambiente do host (macOS)
   - Montagem via `remoteEnv` no `devcontainer.json`
   - Requer exportação manual antes de iniciar

3. **1Password CLI:**
   - Montado via bind mount (se disponível)
   - Permite `op read` dentro do container
   - Requer autenticação prévia no host

### Variáveis Disponíveis no Container

```bash
# Dentro do DevContainer/Codespace:
echo $SHARED_OPENAI_API_KEY      # Injected
echo $SHARED_HUGGINGFACE_TOKEN   # Injected
echo $OPENAI_API_KEY             # Alias de SHARED_*
echo $HF_TOKEN                   # Alias de SHARED_*
```

## 📋 Comandos Úteis

### Verificar Ambiente
```bash
# Versões instaladas
python --version
pip --version
op --version
gh --version

# Secrets configurados
env | grep SHARED_

# Status Git
git status
gh auth status
```

### Executar Auditoria
```bash
# Modo interativo
audit

# Cofre específico
audit --vaults 1p_vps

# Com HuggingFace API
audit --vaults 1p_vps --hf

# Apenas exportar
audit --vaults 1p_vps --export-only
```

### Executar Gradio
```bash
# Iniciar interface web
gradio-dev

# Acessar via port forwarding
# URL será exibida no terminal e VS Code
```

### Sincronizar Secrets
```bash
# Status SSOT
ssot status

# Sync para GitHub (se local)
ssot sync-gh-codespaces

# Sync para HuggingFace
ssot sync-hf-spaces
```

## 🐛 Troubleshooting

### Secrets não disponíveis

**Problema:** `SHARED_*` variáveis vazias

**Solução:**
```bash
# Verificar configuração no GitHub
gh secret list --app codespaces --user

# Recriar Codespace
gh codespace delete <name>
gh codespace create -r senal88/1password-audit-expert

# Ou rebuild container local
# VS Code: Command Palette > Dev Containers: Rebuild Container
```

### 1Password CLI não funciona

**Problema:** `op: command not found` ou `not signed in`

**Solução:**
```bash
# No host (macOS):
eval $(op signin)

# No container:
# 1Password CLI deve ser configurado no HOST primeiro
# O container monta ~/.config/1Password via bind mount
```

### Portas não são expostas

**Problema:** Gradio não acessível em localhost:7860

**Solução:**
```bash
# Verificar portas
lsof -i :7860

# Reconfigurar port forwarding
# VS Code: Command Palette > Forward a Port > 7860
```

### GitHub CLI não autenticado

**Problema:** `gh: To authenticate, please run: gh auth login`

**Solução:**
```bash
# Autenticar dentro do container
gh auth login

# Ou usar token
echo $SHARED_GITHUB_TOKEN | gh auth login --with-token
```

## 📖 Documentação Adicional

- **Projeto:** [README.md](../README.md)
- **Setup:** [SETUP_COMPLETE.md](../SETUP_COMPLETE.md)
- **SSOT:** [ops/bin/ssot](../ops/bin/ssot) --help
- **DevContainers:** https://code.visualstudio.com/docs/devcontainers/containers
- **Codespaces:** https://docs.github.com/en/codespaces

## 🎯 Quick Start

```bash
# 1. Criar Codespace (primeira vez)
gh codespace create -r senal88/1password-audit-expert

# 2. Configurar secrets (se não fez ainda)
# Vá para: https://github.com/settings/codespaces

# 3. Conectar
gh codespace code

# 4. Dentro do Codespace:
audit --help
ssot status
gradio-dev
```

---

**Tudo pronto! Ambiente 100% configurado. 🚀**
