#!/usr/bin/env python3
"""
1Password Security Auditor Expert - CLI Tool
=============================================
Auditoria completa de cofres 1Password com LLM local (Ollama) ou HuggingFace Inference API.

Requisitos:
- 1Password CLI (op) autenticado
- Ollama com modelo configurado OU HuggingFace Pro token

Uso:
    python audit_1password_expert.py                    # Modo interativo
    python audit_1password_expert.py --vaults 1p_vps   # Cofre específico
    python audit_1password_expert.py --all --hf        # Todos cofres via HF API
    python audit_1password_expert.py --export-only     # Apenas exportar JSON
"""

import subprocess
import json
import sys
import os
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

# Configurações
CONFIG = {
    "ollama_model": "1password-auditor",
    "ollama_fallback": "qwen2.5:14b",
    "hf_model": "Qwen/Qwen2.5-72B-Instruct",
    "hf_fallback": "Qwen/Qwen3-8B",
    "max_tokens": 8192,
    "temperature": 0.2,
    "output_dir": Path.home() / "Prompts" / "00_Admin" / "Logs",
}


class Backend(Enum):
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


@dataclass
class AuditResult:
    vaults: list[str]
    total_items: int
    export_data: list[dict]
    report: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))


def log_info(msg: str) -> None:
    print(f"\033[34m[INFO]\033[0m {msg}")


def log_warn(msg: str) -> None:
    print(f"\033[33m[WARN]\033[0m {msg}")


def log_error(msg: str) -> None:
    print(f"\033[31m[ERROR]\033[0m {msg}", file=sys.stderr)


def log_success(msg: str) -> None:
    print(f"\033[32m[OK]\033[0m {msg}")


def check_op_cli() -> bool:
    """Verifica se 1Password CLI está disponível e autenticado."""
    try:
        result = subprocess.run(
            ["op", "whoami", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            user = json.loads(result.stdout)
            log_success(f"1Password CLI autenticado como: {user.get('email', 'N/A')}")
            return True
        log_error("1Password CLI não autenticado. Execute: eval $(op signin)")
        return False
    except FileNotFoundError:
        log_error("1Password CLI (op) não encontrado. Instale: https://1password.com/downloads/command-line/")
        return False
    except subprocess.TimeoutExpired:
        log_error("Timeout ao verificar 1Password CLI")
        return False


def list_vaults() -> list[dict]:
    """Lista todos os cofres disponíveis."""
    result = subprocess.run(
        ["op", "vault", "list", "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def export_vault(vault_name: str, include_secrets: bool = True) -> dict:
    """Exporta todos os items de um cofre com detalhes completos."""
    log_info(f"Exportando cofre '{vault_name}'...")
    
    # Listar items
    result = subprocess.run(
        ["op", "item", "list", "--vault", vault_name, "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    items_summary = json.loads(result.stdout)
    
    # Obter detalhes completos
    items_full = []
    for idx, item in enumerate(items_summary, 1):
        print(f"  ├─ [{idx}/{len(items_summary)}] {item['title'][:50]}...", end="\r")
        
        cmd = ["op", "item", "get", item["id"], "--vault", vault_name, "--format", "json"]
        if include_secrets:
            cmd.append("--reveal")
        
        try:
            detail = subprocess.run(cmd, capture_output=True, text=True, check=True)
            item_data = json.loads(detail.stdout)
            
            # Adicionar análise de senha inline
            for field in item_data.get("fields", []):
                if field.get("type") == "CONCEALED" and field.get("value"):
                    pwd = field["value"]
                    field["_analysis"] = {
                        "length": len(pwd),
                        "has_upper": any(c.isupper() for c in pwd),
                        "has_lower": any(c.islower() for c in pwd),
                        "has_digit": any(c.isdigit() for c in pwd),
                        "has_symbol": any(not c.isalnum() for c in pwd),
                        "hash": hashlib.sha256(pwd.encode()).hexdigest()[:16],
                    }
            
            items_full.append(item_data)
        except subprocess.CalledProcessError as e:
            log_warn(f"Erro ao obter item {item['id']}: {e.stderr}")
    
    print(" " * 80, end="\r")  # Limpar linha
    log_success(f"Exportados {len(items_full)} items de '{vault_name}'")
    
    return {
        "vault_name": vault_name,
        "vault_id": next((v["id"] for v in list_vaults() if v["name"] == vault_name), None),
        "export_date": datetime.now().isoformat(),
        "total_items": len(items_full),
        "items": items_full,
    }


def check_ollama() -> bool:
    """Verifica se Ollama está disponível."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_ollama_model(model: str) -> bool:
    """Verifica se modelo específico está disponível no Ollama."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        return model in result.stdout
    except subprocess.CalledProcessError:
        return False


def create_ollama_model() -> bool:
    """Cria o modelo customizado no Ollama."""
    modelfile_path = Path(__file__).parent.parent / "models" / "Modelfile.1password-auditor"
    if not modelfile_path.exists():
        log_error(f"Modelfile não encontrado: {modelfile_path}")
        return False
    
    log_info("Criando modelo 1password-auditor no Ollama...")
    result = subprocess.run(
        ["ollama", "create", CONFIG["ollama_model"], "-f", str(modelfile_path)],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        log_success("Modelo criado com sucesso")
        return True
    else:
        log_error(f"Erro ao criar modelo: {result.stderr}")
        return False


def audit_with_ollama(data: list[dict], model: str) -> str:
    """Executa auditoria usando Ollama local."""
    try:
        import ollama
    except ImportError:
        log_error("Biblioteca ollama não instalada. Execute: pip install ollama")
        sys.exit(1)
    
    log_info(f"Iniciando análise com Ollama ({model})...")
    
    # Preparar prompt
    prompt = build_audit_prompt(data)
    
    # Salvar prompt para debug
    debug_file = CONFIG["output_dir"] / f"_debug_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    debug_file.write_text(prompt, encoding="utf-8")
    log_info(f"Prompt salvo em: {debug_file}")
    
    # Chamar LLM
    log_info("Processando com LLM (pode levar 1-5 minutos)...")
    
    response = ollama.generate(
        model=model,
        prompt=prompt,
        options={
            "temperature": CONFIG["temperature"],
            "num_predict": CONFIG["max_tokens"],
        },
    )
    
    return response["response"]


def audit_with_huggingface(data: list[dict], model: str) -> str:
    """Executa auditoria usando HuggingFace Inference API."""
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        log_error("Biblioteca huggingface_hub não instalada. Execute: pip install huggingface_hub")
        sys.exit(1)
    
    log_info(f"Iniciando análise com HuggingFace ({model})...")
    
    # Verificar token
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        # Tentar carregar de 1Password
        try:
            result = subprocess.run(
                ["op", "read", "op://1p_macos/HF_TOKEN/credential"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                token = result.stdout.strip()
        except Exception:
            pass
    
    if not token:
        log_error("Token HuggingFace não encontrado. Configure HF_TOKEN ou adicione ao 1Password")
        sys.exit(1)
    
    client = InferenceClient(model=model, token=token)
    
    # Preparar prompt
    prompt = build_audit_prompt(data)
    
    # Salvar prompt para debug
    debug_file = CONFIG["output_dir"] / f"_debug_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    debug_file.write_text(prompt, encoding="utf-8")
    log_info(f"Prompt salvo em: {debug_file}")
    
    log_info("Processando com HuggingFace Inference API...")
    
    response = client.text_generation(
        prompt,
        max_new_tokens=CONFIG["max_tokens"],
        temperature=CONFIG["temperature"],
        do_sample=True,
    )
    
    return response


def build_audit_prompt(data: list[dict]) -> str:
    """Constrói o prompt de auditoria com os dados exportados."""
    total_items = sum(d["total_items"] for d in data)
    vault_names = [d["vault_name"] for d in data]
    
    prompt = f"""# DADOS PARA AUDITORIA DE SEGURANÇA 1PASSWORD

**Data da Exportação:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Cofres Analisados:** {", ".join(vault_names)}
**Total de Items:** {total_items}

---

## DADOS DOS COFRES

"""
    
    for vault_data in data:
        prompt += f"### COFRE: {vault_data['vault_name']}\n"
        prompt += f"**Total:** {vault_data['total_items']} items\n\n"
        prompt += "```json\n"
        
        # Sanitizar dados sensíveis para o prompt (manter análise, remover valores)
        sanitized_items = []
        for item in vault_data["items"]:
            sanitized = {
                "id": item.get("id"),
                "title": item.get("title"),
                "category": item.get("category"),
                "tags": item.get("tags", []),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "fields": [],
            }
            
            for field in item.get("fields", []):
                f_sanitized = {
                    "id": field.get("id"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "purpose": field.get("purpose"),
                }
                
                # Incluir análise de senha sem o valor real
                if "_analysis" in field:
                    f_sanitized["password_analysis"] = field["_analysis"]
                elif field.get("type") != "CONCEALED" and field.get("value"):
                    # Incluir valores não-sensíveis (URLs, usernames, etc.)
                    f_sanitized["value"] = field["value"]
                
                sanitized["fields"].append(f_sanitized)
            
            sanitized_items.append(sanitized)
        
        prompt += json.dumps(sanitized_items, indent=2, ensure_ascii=False)
        prompt += "\n```\n\n"
    
    prompt += """---

## INSTRUÇÕES DE ANÁLISE

Analise TODOS os items acima e gere um relatório de auditoria completo seguindo o formato especificado no system prompt.

**Checklist obrigatório:**
1. Verificar nomenclatura SSOT v2.1 (prefixos de escopo)
2. Validar tags obrigatórias (escopo + tipo)
3. Analisar força de senhas (via password_analysis)
4. Detectar duplicatas (hashes iguais = senhas idênticas)
5. Verificar campos obrigatórios por categoria
6. Identificar items órfãos ou mal categorizados
7. Gerar comandos `op` prontos para correção

**IMPORTANTE:** 
- Ordene issues por severidade (crítico → baixo)
- Cite IDs exatos dos items
- NÃO exponha valores de senhas
- Gere comandos CLI completos para correção
"""
    
    return prompt


def save_report(result: AuditResult) -> Path:
    """Salva o relatório de auditoria."""
    CONFIG["output_dir"].mkdir(parents=True, exist_ok=True)
    
    # Relatório principal
    report_file = CONFIG["output_dir"] / f"1password_audit_{result.timestamp}.md"
    report_file.write_text(result.report, encoding="utf-8")
    
    # Dados exportados (para referência)
    data_file = CONFIG["output_dir"] / f"1password_export_{result.timestamp}.json"
    
    # Remover valores sensíveis antes de salvar
    safe_data = []
    for vault in result.export_data:
        safe_vault = {
            "vault_name": vault["vault_name"],
            "export_date": vault["export_date"],
            "total_items": vault["total_items"],
            "items": [],
        }
        for item in vault["items"]:
            safe_item = {k: v for k, v in item.items() if k != "fields"}
            safe_item["fields"] = []
            for field in item.get("fields", []):
                safe_field = {k: v for k, v in field.items() if k not in ("value", "_analysis")}
                if "_analysis" in field:
                    safe_field["password_analysis"] = field["_analysis"]
                safe_item["fields"].append(safe_field)
            safe_vault["items"].append(safe_item)
        safe_data.append(safe_vault)
    
    data_file.write_text(json.dumps(safe_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return report_file


def interactive_vault_selection(vaults: list[dict]) -> list[str]:
    """Seleção interativa de cofres."""
    print("\n📦 Cofres disponíveis:")
    for i, vault in enumerate(vaults, 1):
        print(f"  {i}. {vault['name']}")
    
    print("\nDigite os números dos cofres (ex: 1,2,3) ou 'all':")
    choice = input("➤ ").strip().lower()
    
    if choice == "all":
        return [v["name"] for v in vaults]
    
    try:
        indices = [int(x.strip()) for x in choice.split(",")]
        return [vaults[i - 1]["name"] for i in indices if 0 < i <= len(vaults)]
    except (ValueError, IndexError):
        log_error("Seleção inválida")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="1Password Security Auditor Expert",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                          # Modo interativo
  %(prog)s --vaults 1p_vps,1p_macos # Cofres específicos
  %(prog)s --all --hf               # Todos cofres via HuggingFace
  %(prog)s --export-only            # Apenas exportar JSON
  %(prog)s --create-model           # Criar modelo Ollama
        """,
    )
    parser.add_argument("--vaults", "-v", help="Cofres separados por vírgula")
    parser.add_argument("--all", "-a", action="store_true", help="Auditar todos os cofres")
    parser.add_argument("--hf", action="store_true", help="Usar HuggingFace Inference API")
    parser.add_argument("--model", "-m", help="Modelo específico (Ollama ou HF)")
    parser.add_argument("--export-only", action="store_true", help="Apenas exportar dados")
    parser.add_argument("--no-secrets", action="store_true", help="Não incluir valores de senhas")
    parser.add_argument("--create-model", action="store_true", help="Criar modelo Ollama")
    parser.add_argument("--output", "-o", help="Diretório de output")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔐 1PASSWORD SECURITY AUDITOR EXPERT")
    print("=" * 60)
    
    # Configurar output
    if args.output:
        CONFIG["output_dir"] = Path(args.output)
    
    # Verificar 1Password CLI
    if not check_op_cli():
        sys.exit(1)
    
    # Criar modelo Ollama se solicitado
    if args.create_model:
        if create_ollama_model():
            log_success("Modelo criado. Execute novamente sem --create-model")
        sys.exit(0)
    
    # Listar cofres
    vaults = list_vaults()
    if not vaults:
        log_error("Nenhum cofre encontrado")
        sys.exit(1)
    
    # Selecionar cofres
    if args.all:
        selected_vaults = [v["name"] for v in vaults]
    elif args.vaults:
        selected_vaults = [v.strip() for v in args.vaults.split(",")]
        # Validar cofres
        valid_names = {v["name"] for v in vaults}
        invalid = set(selected_vaults) - valid_names
        if invalid:
            log_error(f"Cofres não encontrados: {invalid}")
            sys.exit(1)
    else:
        selected_vaults = interactive_vault_selection(vaults)
    
    if not selected_vaults:
        log_error("Nenhum cofre selecionado")
        sys.exit(1)
    
    log_info(f"Cofres selecionados: {', '.join(selected_vaults)}")
    
    # Confirmar exportação com senhas
    include_secrets = not args.no_secrets
    if include_secrets and not args.export_only:
        print("\n⚠️  Esta auditoria analisará valores de senhas.")
        print("   Os dados serão processados localmente e NÃO serão transmitidos.")
        confirm = input("   Confirma? (sim/não): ").strip().lower()
        if confirm != "sim":
            log_warn("Auditoria cancelada")
            sys.exit(0)
    
    # Exportar cofres
    print("\n" + "=" * 60)
    print("FASE 1: EXPORTAÇÃO DE DADOS")
    print("=" * 60)
    
    export_data = []
    for vault_name in selected_vaults:
        try:
            data = export_vault(vault_name, include_secrets=include_secrets)
            export_data.append(data)
        except subprocess.CalledProcessError as e:
            log_error(f"Erro ao exportar '{vault_name}': {e.stderr}")
    
    if not export_data:
        log_error("Nenhum dado exportado")
        sys.exit(1)
    
    total_items = sum(d["total_items"] for d in export_data)
    log_success(f"Total exportado: {total_items} items de {len(export_data)} cofres")
    
    # Apenas exportar?
    if args.export_only:
        result = AuditResult(
            vaults=selected_vaults,
            total_items=total_items,
            export_data=export_data,
        )
        output_file = save_report(result)
        log_success(f"Dados exportados em: {output_file.parent}")
        sys.exit(0)
    
    # Determinar backend
    print("\n" + "=" * 60)
    print("FASE 2: ANÁLISE COM LLM")
    print("=" * 60)
    
    backend = Backend.HUGGINGFACE if args.hf else Backend.OLLAMA
    
    if backend == Backend.OLLAMA:
        if not check_ollama():
            log_warn("Ollama não disponível, usando HuggingFace API")
            backend = Backend.HUGGINGFACE
        else:
            model = args.model or CONFIG["ollama_model"]
            if not check_ollama_model(model):
                log_warn(f"Modelo '{model}' não encontrado, usando fallback")
                model = CONFIG["ollama_fallback"]
                if not check_ollama_model(model):
                    log_warn("Fallback não disponível, usando HuggingFace API")
                    backend = Backend.HUGGINGFACE
    
    # Executar auditoria
    if backend == Backend.OLLAMA:
        model = args.model or CONFIG["ollama_model"]
        if not check_ollama_model(model):
            model = CONFIG["ollama_fallback"]
        report = audit_with_ollama(export_data, model)
    else:
        model = args.model or CONFIG["hf_model"]
        report = audit_with_huggingface(export_data, model)
    
    # Salvar resultado
    print("\n" + "=" * 60)
    print("FASE 3: RELATÓRIO")
    print("=" * 60)
    
    result = AuditResult(
        vaults=selected_vaults,
        total_items=total_items,
        export_data=export_data,
        report=report,
    )
    
    output_file = save_report(result)
    
    log_success(f"Relatório salvo em: {output_file}")
    log_info(f"Tamanho: {len(report):,} caracteres")
    
    # Exibir prévia
    print("\n" + "=" * 60)
    print("PRÉVIA DO RELATÓRIO")
    print("=" * 60)
    print(report[:2000])
    if len(report) > 2000:
        print(f"\n[... mais {len(report) - 2000:,} caracteres ...]")
    
    print("\n" + "=" * 60)
    print("✅ AUDITORIA CONCLUÍDA")
    print("=" * 60)
    print(f"\n👉 Abra o arquivo para ver o relatório completo:")
    print(f"   {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Auditoria interrompida")
        sys.exit(130)
    except Exception as e:
        log_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
