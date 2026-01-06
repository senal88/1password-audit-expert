# GitHub Copilot Instructions - 1Password Audit Expert

## Project Context
This is a security-focused 1Password audit tool with multi-environment secret management.

## Security Rules

### 🔒 Secret Handling
- NEVER suggest hardcoding credentials
- ALWAYS use 1Password CLI references: `op://vault_id/item_id/field`
- NEVER commit .env files with real values
- Suggest `.env.example` with placeholders only

### ✅ Code Patterns
When suggesting code:
1. Use environment variables for secrets
2. Validate inputs before processing
3. Log sensitive operations (without exposing values)
4. Prefer typed interfaces for safety

### 🎯 Nomenclature SSOT v2.1
```python
# Good
PROD_POSTGRES_DB_MAIN = os.getenv("PROD_POSTGRES_PASSWORD")

# Bad
postgres_password = "hardcoded_value"
```

## Tool-Specific Guidelines

### Python (CLI)
```python
# Always use subprocess for 1Password CLI
import subprocess
value = subprocess.run(
    ["op", "read", "op://vault/item/field"],
    capture_output=True, text=True
).stdout.strip()
```

### JavaScript/TypeScript (Gradio)
```typescript
// Use environment variables
const API_KEY = import.meta.env.VITE_API_KEY;
if (!API_KEY) throw new Error("API_KEY not configured");
```

### Bash Scripts
```bash
# Always check op CLI first
if ! op whoami &> /dev/null; then
    echo "❌ 1Password CLI not authenticated"
    exit 1
fi

# Use op read for secrets
SECRET=$(op read "op://vault/item/field")
```

## Deployment Context

### GitHub Codespaces
- Secrets via `gh secret set --app codespaces --user`
- Prefer SHARED_ prefix for multienv
- DevContainer uses `remoteEnv` injection

### HuggingFace Spaces
- Secrets via Space Settings or `HfApi.add_space_secret()`
- Public space = extra caution

### Coolify (VPS)
- Env vars via API `/api/v1/applications/{uuid}/envs`
- Bearer token auth required

## Code Review Priorities

When reviewing PRs:
1. ❌ Block: Hardcoded credentials
2. ⚠️ Warn: Missing input validation
3. ✅ Approve: Proper secret management
4. 💡 Suggest: Type safety improvements

## Quick Commands

### Suggest for Development
```bash
# Local audit
python cli/audit_1password_expert.py --vaults 1p_vps

# Sync secrets to Codespaces
ops/bin/ssot sync-gh-codespaces
```

### Suggest for Deployment
```bash
# Deploy to HF Space
ops/bin/ssot sync-hf-spaces

# Update Coolify
ops/bin/ssot sync-coolify
```

## Do NOT Suggest

- ❌ Storing secrets in git
- ❌ Base64 encoding as "encryption"
- ❌ Committing .env files
- ❌ Using `print()` for secrets
- ❌ Skipping validation

## DO Suggest

- ✅ 1Password CLI integration
- ✅ Type hints and validation
- ✅ Secure logging (mask secrets)
- ✅ Environment-specific configs
- ✅ Automated testing for security

## Error Messages

Prefer actionable error messages:
```python
# Good
raise ValueError(
    "HF_TOKEN not found. "
    "Run: op read op://vault/HF_TOKEN/credential"
)

# Bad
raise ValueError("Token missing")
```

## Testing Guidelines

For security-critical code:
1. Mock 1Password CLI calls
2. Test with invalid inputs
3. Verify no secrets in logs
4. Check error handling

## Remember
This tool handles REAL production credentials. Security > Convenience.
