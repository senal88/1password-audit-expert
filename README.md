# 🔐 1Password Security Auditor Expert

Sistema completo de auditoria de segurança para cofres 1Password com suporte a LLM local (Ollama) e HuggingFace Inference API.

## 📁 Estrutura do Projeto

```plaintext
1password-audit-expert/
├── cli/                          # Ferramenta CLI (auditoria, exportação, integração LLM)
│   ├── audit_1password_expert.py # Script principal CLI
│   └── requirements.txt          # Dependências Python CLI
├── gradio/                       # Interface Web (HuggingFace Space)
│   ├── app.py                    # Aplicação Gradio
│   ├── requirements.txt          # Dependências Web
│   └── README.md                 # Documentação da interface
├── models/                       # Configuração de modelos LLM/Ollama
│   └── Modelfile.1password-auditor  # Modelfile customizado Ollama
├── notebooks/                    # Notebooks Jupyter/Colab (ecolab, exemplos, integração)
│   └── exemplo_ecolab.ipynb      # Exemplo de uso ecolab + Drive
├── ops/                          # Toolkit SSOT (scripts, sync, policy, templates)
│   ├── bin/                      # Scripts executáveis (padronização, sync, apply)
│   ├── state/                    # Estado, logs e auditorias
│   ├── policy/                   # Políticas SSOT e regras de governança
│   ├── templates/                # Templates de padronização e automação
├── raycast/                      # Scripts Raycast para automação rápida
├── .cursor/rules/                # Protocolos Agent para VS Code/Cursor
├── .github/                      # Instruções Copilot, workflows, CI/CD
├── scripts/                      # Scripts de automação e setup
│   └── setup_1password_auditor.sh   # Setup automatizado do ambiente
└── README.md                     # Documentação principal
```

## 📂 Estrutura Google Drive (SSOT)

- Prompts (root) [`1-6egudkhW3ueqNtpQLwR8e4ezY7mZrPd`]
  - 00_Admin (Audit/Logs) [`1Ex3olgm3UkXacuw-06Gp6xdTuy1JP1R2`]
  - 01_System (Core Rules) [`1U8ZSzVFtOHGOB8UuIxA5k7sZlWg8TS7d`]
  - 02_RAG (Knowledge Ingest) [`1SI81O8ESWXx01VtyBdkkWjueITEulOXd`]
  - 03_Templates (Prompting) [`1w1rJYkPNWg00hDKIDmFJfEUZT6BWwOj0`]
  - 05_Workflows (Scripts) [`1CyYdzkGnP61nqbGf4Suf1kQbbDiVocjt`]
  - _upload_claude_desktop [`1FSLvz7PTT6TCdP3Zbjy07eDq_D543mpY`]
  - _upload_notebooklm [`1XMdzyQE6TIOg9DfPBiRWqjXVgk9laiTO`]

**Path local montado:**
`/Users/luiz.sena88/GoogleDrive/Prompts/01_System/...`
`/Users/luiz.sena88/GoogleDrive/Prompts/05_Workflows/...`

## 🔑 Integração Perplexity Pro (VS Code, Cursor, VPS)

### Visual Studio Code

- Extensões instaladas:
  - Perplexity.ai (ghutu.perplexity-ext)
  - Reprompt (kwesinavilot.reprompt)
  - Perplexity AI Assistant (corebytesinc.perplexity-ai-assistant)
- Para autenticar, acesse as configurações da extensão e insira sua Sonar API Key (Pro) conforme padrão seguro:
  - **Nunca exponha a chave diretamente.**
  - Use referência 1Password: `op://<vault_id>/<item>/<field>`
  - Exemplo: `op://gkpsbgizlks2zknwzqpppnb2ze/PERPLEXITY_SONAR/api_key`

### Cursor IDE

- Caso não haja extensão nativa, utilize integração via CLI (veja seção CLI abaixo).
- Configure variáveis de ambiente no projeto ou via 1Password CLI:
  - `export PERPLEXITY_API_KEY="$(op read op://<vault_id>/<item>/<field>)"`

### VPS Ubuntu (CLI)

- Instale o Perplexity CLI conforme documentação oficial.
- Autentique usando a Sonar API Key via 1Password CLI:
  - `export PERPLEXITY_API_KEY="$(op read op://<vault_id>/<item>/<field>)"`
- Nunca salve a chave em texto plano.

### SSOT: Nomenclatura de API Keys no 1Password

| Serviço/Stack         | Nome SSOT 1Password                                    | Exemplo de Referência Completa                                      |
|-----------------------|-------------------------------------------------------|---------------------------------------------------------------------|
| Perplexity Sonar Pro  | PERPLEXITY_SONAR/api_key                              | op://gkpsbgizlks2zknwzqpppnb2ze/PERPLEXITY_SONAR/api_key            |
| OpenAI (global)       | SSOT::SHARED::EXTERNAL::OPENAI/api_key                | op://gkpsbgizlks2zknwzqpppnb2ze/SSOT::SHARED::EXTERNAL::OPENAI/api_key |
| HuggingFace (exemplo) | SSOT::SHARED::EXTERNAL::HUGGINGFACE/api_key           | op://gkpsbgizlks2zknwzqpppnb2ze/SSOT::SHARED::EXTERNAL::HUGGINGFACE/api_key |
| Coolify (token)       | SSOT::SHARED::EXTERNAL::COOLIFY/api_token             | op://gkpsbgizlks2zknwzqpppnb2ze/SSOT::SHARED::EXTERNAL::COOLIFY/api_token |
| GitHub Codespaces     | SSOT::SHARED::EXTERNAL::GITHUB/api_token              | op://gkpsbgizlks2zknwzqpppnb2ze/SSOT::SHARED::EXTERNAL::GITHUB/api_token |

> Sempre use o padrão: `op://<vault_id>/<item>/<field>`
> Prefixo `SSOT::SHARED::EXTERNAL::` para chaves globais multiambiente.
> Para stacks específicas, siga `{ESCOPO}_{SERVICO}_{TIPO}` (ex: PROD_OPENAI_API_KEY).

-- Valor mensal: US$5 (Pro)
-- Sempre armazene a chave no 1Password, nunca em arquivos .env ou scripts.
-- Exemplo de referência segura: `op://gkpsbgizlks2zknwzqpppnb2ze/PERPLEXITY_SONAR/api_key`

---

| Vault ID                      | Nome                | Uso Principal         |
|-------------------------------|---------------------|----------------------|
| zfdghptbnbxjilasq7e2tb3rxi    | 1p_azure            | Secrets Azure/Cloud   |
| gkpsbgizlks2zknwzqpppnb2ze    | 1p_macos            | Dev local/macOS       |
| oa3tidekmeu26nxiier2qbi7v4    | 1p_vps              | Prod/Servidor VPS     |
| syz4hgfg6c62ndrxjmoortzhia    | default importado   | Importação/Legado     |
| 7bgov3zmccio5fxc5v7irhy5k4    | Personal            | Pessoal               |

**Autenticação ativa:** `luiz.sena88@icloud.com`
**URL:** [https://my.1password.com/](https://my.1password.com/)

### Paths principais globais

- **Workspace local (macOS):** `/Users/luiz.sena88/Projects/1password-audit-expert`
- **Google Drive (montado):** `/Users/luiz.sena88/GoogleDrive/Prompts`
- **SSD externo (backup/arquivos antigos):** `/Volumes/SSD_Externo/MFO`
- **VPS (produção):** `/home/luiz/Projects/1password-audit-expert`

> Use sempre referências SSOT: `op://<vault_id>/<item>/<field>`
> Exemplo: `OPENAI_API_KEY="op://gkpsbgizlks2zknwzqpppnb2ze/SSOT::SHARED::EXTERNAL::OPENAI/api_key"`

## 🚀 Quick Start

### Opção 1: Setup Automatizado (Recomendado)

```bash
# Clonar e executar setup
git clone https://huggingface.co/spaces/senal88/1password-audit-expert
cd 1password-audit-expert
chmod +x scripts/setup_1password_auditor.sh
./scripts/setup_1password_auditor.sh
```

### Opção 2: Instalação Manual

```bash
# 1. Instalar dependências
pip install ollama huggingface_hub

# 2. Configurar modelo Ollama (opcional)
ollama pull qwen2.5:14b
ollama create 1password-auditor -f models/Modelfile.1password-auditor

# 3. Autenticar 1Password
eval $(op signin)

# 4. Executar auditoria
python cli/audit_1password_expert.py --vaults 1p_vps
```

## 📋 Uso do CLI

### Comandos Básicos

```bash
# Modo interativo (selecionar cofres)
python audit_1password_expert.py

# Cofres específicos
python audit_1password_expert.py --vaults 1p_vps,1p_macos

# Todos os cofres
python audit_1password_expert.py --all

# Usar HuggingFace API (em vez de Ollama local)
python audit_1password_expert.py --vaults 1p_vps --hf

# Apenas exportar dados (sem análise)
python audit_1password_expert.py --vaults 1p_vps --export-only

# Criar modelo Ollama customizado
python audit_1password_expert.py --create-model
```

### Opções Avançadas

| Opção | Descrição |
|-------|-----------|
| `--vaults`, `-v` | Cofres separados por vírgula |
| `--all`, `-a` | Auditar todos os cofres |
| `--hf` | Usar HuggingFace Inference API |
| `--model`, `-m` | Modelo específico (Ollama ou HF) |
| `--export-only` | Apenas exportar dados JSON |
| `--no-secrets` | Não incluir valores de senhas |
| `--output`, `-o` | Diretório de output |
| `--create-model` | Criar modelo Ollama customizado |

## 🌐 Interface Web (HuggingFace Space)

Acesse: <https://huggingface.co/spaces/senal88/1password-audit-expert>

### Deploy Local

```bash
cd gradio
pip install -r requirements.txt
python app.py
# Acesse: http://localhost:7860
```

## 📊 O que é Analisado

### 1. Nomenclatura (SSOT v2.1)

Padrão obrigatório: `{ESCOPO}_{SERVICO}_{TIPO}[_{QUALIFICADOR}]`

**Escopos válidos:**

- `PROD_` — Produção
- `DEV_` — Desenvolvimento
- `SHARED_` — Compartilhado
- `MACOS_` — Específico macOS
- `VPS_` — Específico servidor
- `AZURE_` — Cloud Azure

### 2. Tags Obrigatórias

- **Escopo:** `production`, `development`, `staging`, `global`
- **Tipo:** `database`, `api_key`, `service_account`, `ssh_key`, `oauth`, `certificate`

### 3. Segurança de Senhas

| Critério | Mínimo | Ideal |
|----------|--------|-------|
| Comprimento | 15 chars | 24+ chars |
| Complexidade | Letras+números | +símbolos |
| Idade máxima | 180 dias | 90 dias |
| Duplicatas | PROIBIDO | — |

**Padrões fracos detectados:**

- Sequências: `123`, `abc`, `qwerty`
- Anos: `2023`, `2024`, `2025`
- Palavras comuns: `password`, `admin`, `root`

### 4. Campos Obrigatórios por Categoria

| Categoria | Campos Requeridos |
|-----------|-------------------|
| Login | username, password, url |
| Database | host, port, username, password, database |
| API Credential | api_key ou credential |
| Server | host, port, username |
| SSH Key | private_key, public_key |

## 🔒 Privacidade e Segurança

### CLI Local (Máxima Segurança)

- 100% offline com Ollama
- Dados nunca saem da máquina
- Senhas em memória apenas durante análise

### Interface Web

- Dados processados via HuggingFace Inference API
- Sem armazenamento permanente
- Recomendado apenas para dados não-críticos

## 🤖 Modelos Suportados

### Ollama (Local)

- `1password-auditor` — Modelo customizado (recomendado)
- `qwen2.5:14b` — Fallback (128k context)
- `qwen3:8b` — Alternativa leve

### HuggingFace Inference API

- `Qwen/Qwen2.5-72B-Instruct` — Recomendado
- `Qwen/Qwen3-8B` — Rápido
- `deepseek-ai/DeepSeek-V3.2` — Avançado
- `meta-llama/Llama-3.1-70B-Instruct` — Alternativa

## 📄 Exemplo de Relatório

```markdown
# 📊 Relatório de Auditoria 1Password

**Data:** 2026-01-03 10:30:00
**Cofres:** 1p_vps, 1p_macos
**Total Items:** 68

## 📈 RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| Taxa de Conformidade | 61.8% |
| Issues Críticas | 5 |
| Senhas Duplicadas | 3 grupos |

## 🚨 CRÍTICO

### [abc123xyz] postgres
**Problema:** Senha com 8 caracteres contendo padrão "1234"
**Correção:**
\`\`\`bash
op item edit abc123xyz 'title=PROD_POSTGRES_DB_MAIN' --vault 1p_vps
op item edit abc123xyz --generate-password='letters,digits,symbols,24' --vault 1p_vps
\`\`\`
```

## 📝 Governança SSOT (Padrão Multiambiente)

### Ambiente e parâmetros considerados

- **Repo**: `https://github.com/senal88/prompts-ssot.git`
- **Dev local**: **macOS Silicon Tahoe 26.2** (zsh), 1Password CLI autenticado (`op whoami` OK), vaults existentes: `1p_azure`, `1p_macos`, `1p_vps`, `default importado`, `Personal`
- **Prod**: **VPS Ubuntu 24.04** (Coolify), acesso por SSH (porta 22)
- **Padrão de nomenclatura**: **SSoT** em 1Password + distribuição multiambiente via **prefixo `SHARED_`** (ex.: `SHARED_OPENAI_API_KEY`) e aliases locais não-`SHARED_` quando exigido por ferramentas
- **Ferramentas alvo**: DevContainer/Codespaces, Cursor/VS Code, GitHub secrets (Codespaces), Hugging Face Spaces, Coolify envs, SSH agent (1Password)

Fontes oficiais utilizadas (exemplos chave):

- 1Password CLI: `op item edit`, `op item get`, secret references, `op run`, `op inject` ([developer.1password.com][1])
- DevContainers env vars / substituição `${localEnv:...}` e `remoteEnv` ([Visual Studio Code][2])
- Raycast Script Commands + metadados ([Raycast Manual][3])
- GitHub CLI Codespaces secrets (`gh secret set --app codespaces --user`) ([GitHub CLI][4])
- Hugging Face Spaces secrets e `huggingface_hub.HfApi.add_space_secret` ([Hugging Face][5])
- Coolify env vars (conceito + API bearer + endpoint de update env) ([Coolify][6])
- 1Password SSH agent (config file + IdentityAgent) ([developer.1password.com][7])

---

### Padrão operacional (LLM-friendly) para “coletar → padronizar → aplicar”

#### Regras de ouro (para LLM/Agent no Cursor/VS Code)

1. **Nunca imprimir valores de secrets** em stdout/stderr; usar `op read` somente em pipe direto para o consumidor (GitHub/HF/Coolify).
2. **Não depender de nomes** de vault/item a longo prazo: migrar referências `op://...` para **IDs** (vault_id/item_id), pois secret references suportam identificadores ([developer.1password.com][8]).
3. **`SHARED_` é a fonte** para integração (Codespaces/CI/IDEs); `OPENAI_API_KEY` etc. podem ser **aliases derivados** em runtime (sem duplicar valor em arquivos).
4. **DevContainer**: `remoteEnv` pode referenciar variáveis existentes do ambiente com `${localEnv:VAR}` e `${containerEnv:VAR}` ([Visual Studio Code][2]).
5. **Execução segura**: `op run` mascara secrets por padrão; manter masking (não usar `OP_RUN_NO_MASKING`) ([developer.1password.com][9]).

---

### Instalação do toolkit de padronização (cria arquivos no repo)

Execute no root do repo clonado:

```bash
cd {{REPO_ROOT}}

mkdir -p ops/bin ops/state ops/policy ops/templates raycast .cursor/rules .github

# ... (ver scripts completos no padrão SSOT)
```

---

### Scripts de padronização (prontos)

#### 1) Migrar `op://...` para IDs (vault_id/item_id) sem quebrar governança

Secret references suportam identificadores; `op item get` e `op item edit` são a base de manipulação ([developer.1password.com][8]).

#### 2) Normalizar `.devcontainer/devcontainer.json` para `SHARED_*` (sem duplicar valores)

`remoteEnv` e substituições `${localEnv:VAR}`/`${containerEnv:VAR}` são suportadas conforme documentação do Dev Containers/VS Code ([Visual Studio Code][2]).

#### 3) Sincronizar 1Password → GitHub Codespaces (user secrets) via `gh`

`gh secret set` suporta `--app codespaces` e nível **user** (`--user`) ([GitHub CLI][4]).

#### 4) Sincronizar 1Password → Hugging Face Spaces (secrets) via `huggingface_hub`

Hugging Face recomenda secrets por Settings e expõe como env vars; `HfApi.add_space_secret` adiciona/atualiza secret ([Hugging Face][5]).

#### 5) Sincronizar 1Password → Coolify (env vars) via API

Coolify: autenticação por **Bearer token** e endpoint base `/api/v1` ([Coolify][6]).

---

### Integração macOS: zsh/bash + 1Password SSH Agent (sem vazamento)

#### SSH Agent 1Password

- O 1Password SSH agent pode ser configurado com `IdentityAgent` em `~/.ssh/config` ([developer.1password.com][12]).

- Arquivo de controle fino do agent: `~/.config/1Password/ssh/agent.toml` ([developer.1password.com][7]).

---

### Integração Linux (VPS Ubuntu): bash + padrões de ambiente

---

### Raycast: scripts prontos para “executar padronização” com 1 tecla

Raycast Script Commands suportam metadados no header ([GitHub][13]).

---

### Instruções “Agent Protocol” para Cursor/VS Code (colhe dados e aplica sem erro)

#### `.cursor/rules/90_ssot_agent_protocol.mdc`

---

### `.github/copilot-instructions.md` (opcional, mesma lógica para Copilot)

---

### Execução (sem ambiguidade)

#### No repo (padronização estrutural)

```bash
cd {{REPO_ROOT}}
ops/bin/ssot apply-all
```

#### macOS (shell + SSH agent)

```bash
cd {{REPO_ROOT}}
ops/bin/ssot shell-macos
```

#### VPS Ubuntu (shell profile)

```bash
cd {{REPO_ROOT}}
SUDO=sudo ops/bin/ssot shell-linux
```

#### Distribuição de secrets (requer map sem placeholders)

```bash
cd {{REPO_ROOT}}
ops/bin/ssot sync-gh-codespaces
ops/bin/ssot sync-hf-spaces
COOLIFY_BASE_URL="{{COOLIFY_BASE_URL}}" COOLIFY_API_TOKEN="{{COOLIFY_API_TOKEN}}" ops/bin/ssot sync-coolify
```

---

### Resultado final (o que este padrão elimina)

- **Evita repetição de “governança errada”** por dependência de nomes (migrando refs para **IDs**) ([developer.1password.com][8])
- **Evita vazamento acidental** em logs/prints, mantendo o fluxo via `op run`/pipes ([developer.1password.com][9])
- **Evita divergência entre Dev/Prod** ao centralizar em `SHARED_*` + distribuição determinística (GitHub/HF/Coolify) ([GitHub CLI][4])
- **Evita fricção no Cursor/VS Code** ao garantir secrets plaintext no ambiente (Codespaces) e não refs “op://” onde IDE exige valor real

Implementação entregue com scripts completos, determinísticos e prontos para execução conforme comandos acima.

[1]: https://developer.1password.com/docs/cli/item-edit/?utm_source=chatgpt.com
[2]: https://code.visualstudio.com/remote/advancedcontainers/environment-variables?utm_source=chatgpt.com
[3]: https://manual.raycast.com/script-commands?utm_source=chatgpt.com
[4]: https://cli.github.com/manual/gh_secret_set?utm_source=chatgpt.com
[5]: https://huggingface.co/docs/hub/en/spaces-overview?utm_source=chatgpt.com
[6]: https://coolify.io/docs/api-reference/authorization?utm_source=chatgpt.com
[7]: https://developer.1password.com/docs/ssh/agent/config?utm_source=chatgpt.com
[8]: https://developer.1password.com/docs/cli/secret-reference-syntax?utm_source=chatgpt.com
[9]: https://developer.1password.com/docs/cli/reference/commands/run?utm_source=chatgpt.com
[12]: https://developer.1password.com/docs/ssh/get-started?utm_source=chatgpt.com
[13]: https://github.com/raycast/script-commands

## 📄 Licença

Apache 2.0

## 🤝 Contribuições

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

**Autor:** senal88
**Projeto:** MFO Platform Governance
**Versão:** 1.0.0
