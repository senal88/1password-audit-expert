---
title: 1Password Security Auditor Expert
emoji: 🔐
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Auditoria automatizada de segurança para cofres 1Password
tags:
  - security
  - audit
  - 1password
  - devops
  - governance
---

# 🔐 1Password Security Auditor Expert

Auditoria automatizada de segurança para cofres 1Password usando LLMs.

## ✨ Funcionalidades

- **Análise de Nomenclatura:** Validação contra padrão SSOT v2.1
- **Segurança de Senhas:** Comprimento, complexidade, padrões fracos
- **Detecção de Duplicatas:** Senhas idênticas entre items
- **Validação de Tags:** Escopo e tipo obrigatórios
- **Campos Obrigatórios:** Por categoria (Database, API, SSH, etc.)
- **Comandos CLI:** `op item edit` prontos para correção

## 🚀 Como Usar

### Via Interface Web

1. Exporte seu cofre 1Password:
   ```bash
   eval $(op signin)
   op item list --vault SEU_COFRE --format json > export.json
   ```

2. Cole o JSON na interface

3. Configure o modelo e execute a auditoria

### Via CLI Local (Recomendado para Privacidade)

```bash
git clone https://huggingface.co/spaces/senal88/1password-audit-expert
cd 1password-audit-expert/cli
pip install ollama huggingface_hub
python audit_1password_expert.py --vaults 1p_vps,1p_macos
```

## 🔒 Privacidade

- **Interface Web:** Dados processados via HuggingFace Inference API
- **CLI Local:** 100% offline com Ollama (recomendado para dados sensíveis)

## 📋 Padrões de Governança

### Nomenclatura SSOT v2.1

```
{ESCOPO}_{SERVICO}_{TIPO}[_{QUALIFICADOR}]
```

**Escopos válidos:** `PROD_`, `DEV_`, `SHARED_`, `MACOS_`, `VPS_`, `AZURE_`

### Tags Obrigatórias

- **Escopo:** production, development, staging, global
- **Tipo:** database, api_key, service_account, ssh_key, oauth, certificate

### Requisitos de Senha

| Critério | Mínimo | Ideal |
|----------|--------|-------|
| Comprimento | 15 chars | 24+ chars |
| Complexidade | Letras+números | +símbolos |
| Idade máxima | 180 dias | 90 dias |

## 🛠️ Modelos Suportados

| Modelo | Uso Recomendado |
|--------|-----------------|
| Qwen2.5-72B | Análises completas (recomendado) |
| Qwen3-8B | Análises rápidas |
| DeepSeek-V3.2 | Análises avançadas |
| Llama 3.1 70B | Alternativa |

## 📄 Licença

Apache 2.0

## 🤝 Contribuições

PRs são bem-vindos! Abra uma issue para discussão antes de grandes mudanças.

---

**Autor:** senal88  
**Projeto:** MFO Platform Governance
