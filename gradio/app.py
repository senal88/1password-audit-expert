#!/usr/bin/env python3
"""
1Password Security Auditor Expert - Gradio Interface
======================================================
Interface gráfica profissional para auditoria de cofres 1Password.

Deploy: HuggingFace Spaces (senal88/1password-audit-expert)
"""

import json
import hashlib
import re
from datetime import datetime
from typing import Optional

import gradio as gr
from huggingface_hub import InferenceClient

# Configuração
CONFIG = {
    "title": "🔐 1Password Security Auditor Expert",
    "description": """
    **Auditoria automatizada de segurança para cofres 1Password**
    
    Cole o JSON exportado do seu cofre 1Password e receba um relatório completo de:
    - Violações de nomenclatura (SSOT v2.1)
    - Problemas de segurança de senhas
    - Tags ausentes ou incorretas
    - Campos obrigatórios faltantes
    - Duplicatas e conflitos
    - Comandos CLI prontos para correção
    
    **⚠️ Privacidade:** Os dados são processados via HuggingFace Inference API. 
    Para máxima segurança, use a versão CLI local com Ollama.
    """,
    "models": {
        "Qwen2.5-72B (Recomendado)": "Qwen/Qwen2.5-72B-Instruct",
        "Qwen3-8B (Rápido)": "Qwen/Qwen3-8B",
        "DeepSeek-V3.2 (Avançado)": "deepseek-ai/DeepSeek-V3.2",
        "Llama 3.1 70B": "meta-llama/Llama-3.1-70B-Instruct",
    },
    "max_tokens": 8192,
    "temperature": 0.2,
}

# System prompt do auditor
SYSTEM_PROMPT = """Você é um **Auditor Expert de Segurança** especializado em análise de cofres 1Password.

## REGRAS DE ANÁLISE

### 1. NOMENCLATURA (SSOT v2.1)
Padrão: `{ESCOPO}_{SERVICO}_{TIPO}[_{QUALIFICADOR}]`
Escopos: PROD_, DEV_, SHARED_, MACOS_, VPS_, AZURE_

### 2. TAGS OBRIGATÓRIAS
- Escopo: production, development, staging, global
- Tipo: database, api_key, service_account, ssh_key, oauth, certificate

### 3. SEGURANÇA DE SENHAS
- Mínimo: 15 caracteres
- Ideal: 24+ caracteres com símbolos
- Idade máxima: 180 dias
- Duplicatas: PROIBIDO

### 4. CAMPOS OBRIGATÓRIOS
- Login: username, password, url
- Database: host, port, username, password, database
- API Credential: api_key
- SSH Key: private_key, public_key

## FORMATO DE OUTPUT

Gere um relatório Markdown com:
1. Resumo executivo (tabela de métricas)
2. Issues críticas (com comandos `op` para correção)
3. Issues de alta prioridade
4. Issues médias e baixas
5. Items conformes
6. Plano de ação prioritário
7. Estatísticas detalhadas

**REGRAS:**
- Cite IDs exatos
- Gere comandos `op item edit` prontos
- Ordene por severidade
- NÃO exponha valores de senhas
"""


def sanitize_json_input(json_text: str) -> tuple[list[dict], str]:
    """Sanitiza e valida input JSON."""
    try:
        # Tentar parse
        data = json.loads(json_text)
        
        # Normalizar estrutura
        if isinstance(data, dict):
            if "items" in data:
                items = data["items"]
            else:
                items = [data]
        elif isinstance(data, list):
            items = data
        else:
            return [], "Formato inválido: esperado objeto ou array JSON"
        
        # Processar items
        processed = []
        password_hashes = {}
        
        for item in items:
            processed_item = {
                "id": item.get("id", f"unknown_{len(processed)}"),
                "title": item.get("title", "Sem título"),
                "category": item.get("category", "UNKNOWN"),
                "tags": item.get("tags", []),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "fields": [],
            }
            
            for field in item.get("fields", []):
                f_processed = {
                    "id": field.get("id"),
                    "label": field.get("label", ""),
                    "type": field.get("type", "STRING"),
                    "purpose": field.get("purpose"),
                }
                
                value = field.get("value", "")
                
                # Analisar senhas
                if field.get("type") == "CONCEALED" and value:
                    pwd_hash = hashlib.sha256(value.encode()).hexdigest()[:16]
                    
                    # Detectar duplicatas
                    if pwd_hash in password_hashes:
                        password_hashes[pwd_hash].append(processed_item["id"])
                    else:
                        password_hashes[pwd_hash] = [processed_item["id"]]
                    
                    f_processed["password_analysis"] = {
                        "length": len(value),
                        "has_upper": any(c.isupper() for c in value),
                        "has_lower": any(c.islower() for c in value),
                        "has_digit": any(c.isdigit() for c in value),
                        "has_symbol": any(not c.isalnum() for c in value),
                        "hash": pwd_hash,
                        "patterns": detect_weak_patterns(value),
                    }
                elif field.get("type") != "CONCEALED":
                    f_processed["value"] = value[:200]  # Truncar valores longos
                
                processed_item["fields"].append(f_processed)
            
            processed.append(processed_item)
        
        # Marcar duplicatas
        duplicates = {h: ids for h, ids in password_hashes.items() if len(ids) > 1}
        if duplicates:
            for item in processed:
                for field in item["fields"]:
                    if "password_analysis" in field:
                        h = field["password_analysis"]["hash"]
                        if h in duplicates:
                            field["password_analysis"]["is_duplicate"] = True
                            field["password_analysis"]["duplicate_ids"] = duplicates[h]
        
        return processed, ""
        
    except json.JSONDecodeError as e:
        return [], f"JSON inválido: {e}"
    except Exception as e:
        return [], f"Erro ao processar: {e}"


def detect_weak_patterns(password: str) -> list[str]:
    """Detecta padrões fracos em senhas."""
    patterns = []
    pwd_lower = password.lower()
    
    # Sequências
    sequences = ["123", "234", "345", "456", "567", "678", "789", "890",
                 "abc", "bcd", "cde", "def", "qwerty", "asdf"]
    for seq in sequences:
        if seq in pwd_lower:
            patterns.append(f"sequência '{seq}'")
    
    # Anos
    years = re.findall(r"20[12][0-9]|19[89][0-9]", password)
    if years:
        patterns.append(f"ano {years[0]}")
    
    # Palavras comuns
    weak_words = ["password", "admin", "root", "secret", "login", "user", "test"]
    for word in weak_words:
        if word in pwd_lower:
            patterns.append(f"palavra '{word}'")
    
    # Repetições
    if re.search(r"(.)\1{2,}", password):
        patterns.append("caracteres repetidos")
    
    return patterns


def build_prompt(items: list[dict], vault_name: str = "Cofre") -> str:
    """Constrói o prompt de auditoria."""
    return f"""# DADOS PARA AUDITORIA DE SEGURANÇA 1PASSWORD

**Data:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Cofre:** {vault_name}
**Total de Items:** {len(items)}

## DADOS DO COFRE

```json
{json.dumps(items, indent=2, ensure_ascii=False)}
```

---

Analise TODOS os items acima e gere um relatório de auditoria completo.

**Checklist:**
1. Verificar nomenclatura SSOT v2.1
2. Validar tags obrigatórias
3. Analisar força de senhas (via password_analysis)
4. Detectar duplicatas (is_duplicate=true)
5. Verificar campos obrigatórios
6. Gerar comandos `op` para correção

**IMPORTANTE:** Ordene por severidade, cite IDs exatos, NÃO exponha senhas."""


def run_audit(
    json_input: str,
    vault_name: str,
    model_choice: str,
    hf_token: Optional[str],
    progress=gr.Progress()
) -> tuple[str, str]:
    """Executa a auditoria completa."""
    
    progress(0.1, desc="Validando input...")
    
    # Validar input
    items, error = sanitize_json_input(json_input)
    if error:
        return f"❌ **Erro de validação:** {error}", ""
    
    if not items:
        return "❌ **Erro:** Nenhum item encontrado no JSON", ""
    
    progress(0.2, desc=f"Processados {len(items)} items...")
    
    # Preparar prompt
    prompt = build_prompt(items, vault_name)
    
    progress(0.3, desc="Conectando ao modelo...")
    
    # Obter modelo
    model_id = CONFIG["models"].get(model_choice, CONFIG["models"]["Qwen2.5-72B (Recomendado)"])
    
    # Verificar token
    token = hf_token or None
    if not token:
        import os
        token = os.environ.get("HF_TOKEN")
    
    if not token:
        return "❌ **Erro:** Token HuggingFace não fornecido. Cole seu token ou configure HF_TOKEN.", ""
    
    progress(0.4, desc=f"Iniciando análise com {model_choice}...")
    
    try:
        client = InferenceClient(model=model_id, token=token)
        
        # Construir mensagens
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        
        progress(0.5, desc="Processando com LLM (pode levar 1-2 minutos)...")
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=CONFIG["max_tokens"],
            temperature=CONFIG["temperature"],
        )
        
        report = response.choices[0].message.content
        
        progress(0.9, desc="Finalizando relatório...")
        
        # Gerar estatísticas
        stats = generate_stats(items)
        
        progress(1.0, desc="Concluído!")
        
        return report, stats
        
    except Exception as e:
        return f"❌ **Erro na API:** {str(e)}", ""


def generate_stats(items: list[dict]) -> str:
    """Gera estatísticas dos items processados."""
    total = len(items)
    
    # Contadores
    has_tags = sum(1 for i in items if i.get("tags"))
    categories = {}
    password_lengths = []
    weak_passwords = 0
    duplicates = set()
    
    for item in items:
        cat = item.get("category", "UNKNOWN")
        categories[cat] = categories.get(cat, 0) + 1
        
        for field in item.get("fields", []):
            if "password_analysis" in field:
                pa = field["password_analysis"]
                password_lengths.append(pa["length"])
                
                if pa["length"] < 15 or pa.get("patterns"):
                    weak_passwords += 1
                
                if pa.get("is_duplicate"):
                    duplicates.add(pa["hash"])
    
    # Formatar
    avg_pwd_len = sum(password_lengths) / len(password_lengths) if password_lengths else 0
    
    stats = f"""### 📊 Estatísticas do Input

| Métrica | Valor |
|---------|-------|
| Total de Items | {total} |
| Com Tags | {has_tags} ({has_tags/total*100:.1f}%) |
| Sem Tags | {total - has_tags} |
| Senhas Analisadas | {len(password_lengths)} |
| Comprimento Médio | {avg_pwd_len:.1f} chars |
| Senhas Fracas | {weak_passwords} |
| Grupos Duplicados | {len(duplicates)} |

### Por Categoria
| Categoria | Quantidade |
|-----------|------------|
"""
    
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        stats += f"| {cat} | {count} |\n"
    
    return stats


def create_sample_json() -> str:
    """Retorna JSON de exemplo para demonstração."""
    return json.dumps([
        {
            "id": "abc123xyz",
            "title": "postgres",
            "category": "DATABASE",
            "tags": [],
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-06-20T15:30:00Z",
            "fields": [
                {"id": "f1", "label": "username", "type": "STRING", "value": "admin"},
                {"id": "f2", "label": "password", "type": "CONCEALED", "value": "Pass1234"},
                {"id": "f3", "label": "host", "type": "STRING", "value": "db.example.com"},
                {"id": "f4", "label": "port", "type": "STRING", "value": "5432"},
            ]
        },
        {
            "id": "def456uvw",
            "title": "API-Key-Production",
            "category": "API_CREDENTIAL",
            "tags": ["api"],
            "created_at": "2024-03-10T08:00:00Z",
            "updated_at": "2024-03-10T08:00:00Z",
            "fields": [
                {"id": "f5", "label": "credential", "type": "CONCEALED", "value": "sk_live_abcdef123456"},
            ]
        },
        {
            "id": "ghi789rst",
            "title": "redis-cache",
            "category": "DATABASE",
            "tags": ["cache"],
            "created_at": "2024-02-20T12:00:00Z",
            "updated_at": "2024-08-15T09:00:00Z",
            "fields": [
                {"id": "f6", "label": "password", "type": "CONCEALED", "value": "Pass1234"},
                {"id": "f7", "label": "host", "type": "STRING", "value": "redis.example.com"},
            ]
        }
    ], indent=2)


# Interface Gradio
with gr.Blocks(
    title=CONFIG["title"],
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
    ),
    css="""
    .main-title { text-align: center; margin-bottom: 20px; }
    .report-output { font-family: 'SF Mono', 'Consolas', monospace; }
    .stats-output { background: #f5f5f5; padding: 15px; border-radius: 8px; }
    """
) as demo:
    
    gr.Markdown(f"# {CONFIG['title']}", elem_classes=["main-title"])
    gr.Markdown(CONFIG["description"])
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Configuração")
            
            vault_name = gr.Textbox(
                label="Nome do Cofre",
                placeholder="Ex: 1p_vps, 1p_macos",
                value="Cofre Principal",
            )
            
            model_choice = gr.Dropdown(
                label="Modelo LLM",
                choices=list(CONFIG["models"].keys()),
                value="Qwen2.5-72B (Recomendado)",
            )
            
            hf_token = gr.Textbox(
                label="Token HuggingFace (opcional se HF_TOKEN configurado)",
                placeholder="hf_...",
                type="password",
            )
            
            with gr.Row():
                audit_btn = gr.Button("🔍 Executar Auditoria", variant="primary", scale=2)
                sample_btn = gr.Button("📋 Carregar Exemplo", scale=1)
        
        with gr.Column(scale=2):
            gr.Markdown("### 📥 Input: JSON do 1Password")
            
            json_input = gr.Code(
                label="Cole o JSON exportado (op item list --format json)",
                language="json",
                lines=15,
            )
    
    gr.Markdown("---")
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Relatório de Auditoria")
            report_output = gr.Markdown(
                label="Relatório",
                elem_classes=["report-output"],
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 📈 Estatísticas")
            stats_output = gr.Markdown(
                label="Estatísticas",
                elem_classes=["stats-output"],
            )
    
    # Eventos
    audit_btn.click(
        fn=run_audit,
        inputs=[json_input, vault_name, model_choice, hf_token],
        outputs=[report_output, stats_output],
    )
    
    sample_btn.click(
        fn=create_sample_json,
        outputs=[json_input],
    )
    
    # Exemplos
    gr.Markdown("---")
    gr.Markdown("### 📚 Como Usar")
    gr.Markdown("""
    1. **Exporte seus dados do 1Password:**
       ```bash
       # Autenticar
       eval $(op signin)
       
       # Exportar cofre (com senhas reveladas)
       op item list --vault 1p_vps --format json > export.json
       
       # Para detalhes completos de cada item:
       for id in $(op item list --vault 1p_vps --format json | jq -r '.[].id'); do
           op item get "$id" --vault 1p_vps --format json --reveal
       done | jq -s '.' > export_full.json
       ```
    
    2. **Cole o JSON no campo de input**
    
    3. **Configure o nome do cofre e modelo**
    
    4. **Clique em "Executar Auditoria"**
    
    5. **Revise o relatório e aplique as correções sugeridas**
    
    ---
    
    **🔒 Privacidade:** Para máxima segurança, use a versão CLI local:
    ```bash
    git clone https://huggingface.co/spaces/senal88/1password-audit-expert
    cd 1password-audit-expert/cli
    python audit_1password_expert.py --vaults 1p_vps
    ```
    """)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
