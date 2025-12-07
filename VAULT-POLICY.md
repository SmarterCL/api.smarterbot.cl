# 🔐 VAULT-POLICY — SmarterOS Multi-Tenant Security

## 🎯 Objetivo
Aislar secretos por RUT chileno usando HashiCorp Vault, con políticas dinámicas y rotación automática.

---

## 🧱 Estructura de Namespaces

```
vault/
├── tenant/
│   ├── 76953480-3/          # RUT empresa 1
│   │   ├── shopify/
│   │   │   ├── api_key
│   │   │   ├── api_secret
│   │   │   └── webhook_secret
│   │   ├── odoo/
│   │   │   ├── username
│   │   │   ├── password
│   │   │   └── database
│   │   ├── chatwoot/
│   │   │   ├── api_token
│   │   │   └── inbox_id
│   │   ├── n8n/
│   │   │   └── workflow_token
│   │   └── whatsapp/
│   │       ├── phone_number
│   │       └── api_token
│   └── 77234567-8/          # RUT empresa 2
│       └── ...
└── system/
    ├── clerk/
    │   ├── secret_key
    │   └── publishable_key
    ├── supabase/
    │   ├── url
    │   └── service_role
    └── openai/
        └── api_key
```

---

## 🔒 Policy por Tenant

### Política Base (HCL)
```hcl
# Policy: tenant-76953480-3
path "secret/data/tenant/76953480-3/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/tenant/76953480-3/*" {
  capabilities = ["list", "read", "delete"]
}

# Deny access a otros tenants
path "secret/data/tenant/*" {
  capabilities = ["deny"]
}
```

### Política de Servicios
```hcl
# Policy: service-api-gateway
path "secret/data/tenant/+/shopify/*" {
  capabilities = ["read"]
}

path "secret/data/tenant/+/odoo/*" {
  capabilities = ["read"]
}

path "secret/data/system/*" {
  capabilities = ["read"]
}
```

---

## 🔑 Tokens por Servicio

| Servicio        | Policy Applied          | TTL    | Renewable |
|-----------------|-------------------------|--------|-----------|
| API Gateway     | service-api-gateway     | 24h    | Yes       |
| Botpress        | service-botpress        | 12h    | Yes       |
| n8n             | service-n8n             | 24h    | Yes       |
| Chatwoot        | service-chatwoot        | 24h    | Yes       |
| Portal (Admin)  | admin-full-access       | 1h     | Yes       |

---

## 🛡️ MCP + HMAC Integration

### Request Signature
```python
import hmac
import hashlib

def sign_request(tenant_id: str, payload: dict, vault_secret: str):
    message = f"{tenant_id}:{json.dumps(payload)}"
    signature = hmac.new(
        vault_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### Validation
```python
def validate_signature(tenant_id: str, payload: dict, signature: str):
    vault_secret = vault.read(f"secret/tenant/{tenant_id}/mcp/hmac_key")
    expected = sign_request(tenant_id, payload, vault_secret)
    return hmac.compare_digest(signature, expected)
```

---

## 📦 Secrets por Servicio

### Shopify
```bash
vault kv put secret/tenant/76953480-3/shopify \
  api_key="shpat_xxxx" \
  api_secret="shpss_xxxx" \
  webhook_secret="whsec_xxxx" \
  store_url="tienda.myshopify.com"
```

### Odoo
```bash
vault kv put secret/tenant/76953480-3/odoo \
  url="https://odoo.smarterbot.cl" \
  database="odoo" \
  username="76953480-3@odoo" \
  password="secure_pass" \
  company_id="3"
```

### WhatsApp (Chatwoot)
```bash
vault kv put secret/tenant/76953480-3/whatsapp \
  phone_number="+56979540471" \
  api_token="cwt_xxxx" \
  inbox_id="14" \
  provider="360dialog"
```

---

## 🔄 Rotación Automática

### Configuración
```hcl
path "secret/data/tenant/+/shopify/api_key" {
  rotation_period = "30d"
  notification_webhook = "https://api.smarterbot.cl/vault/rotation"
}
```

### Webhook Notification
```json
{
  "event": "secret_rotated",
  "tenant_id": "76953480-3",
  "path": "secret/tenant/76953480-3/shopify/api_key",
  "timestamp": "2025-11-23T12:00:00Z"
}
```

---

## 🧪 Testing

### Read Secret
```bash
vault kv get secret/tenant/76953480-3/shopify
```

### Policy Test
```bash
vault policy read tenant-76953480-3
vault token capabilities secret/data/tenant/76953480-3/shopify
```

### Audit Log
```bash
vault audit enable file file_path=/var/log/vault/audit.log
```

---

## 📝 Ejemplo E2E: Webhook Shopify

1. Shopify envía webhook → API Gateway
2. API valida HMAC usando Vault secret
3. Si válido → procesa orden
4. Guarda en Supabase con tenant_id
5. Dispara n8n workflow con token de Vault
6. n8n conecta a Odoo usando credentials de Vault

---

## 🚀 Onboarding Tenant

```python
def create_tenant_vault(tenant_id: str):
    # Create namespace
    vault.create_namespace(f"tenant/{tenant_id}")
    
    # Create policy
    policy = generate_tenant_policy(tenant_id)
    vault.create_policy(f"tenant-{tenant_id}", policy)
    
    # Generate tokens
    tokens = {
        "shopify": vault.generate_secret(),
        "odoo": vault.generate_secret(),
        "whatsapp": vault.generate_secret()
    }
    
    # Store secrets
    for service, secret in tokens.items():
        vault.write(
            f"secret/tenant/{tenant_id}/{service}/api_key",
            value=secret
        )
    
    return tokens
```

---

## 🔐 Security Best Practices

✔ Un token por servicio  
✔ TTL corto (< 24h)  
✔ Rotación automática  
✔ Audit logs habilitado  
✔ HMAC en todos los webhooks  
✔ Deny por defecto  
✔ Policies por RUT  
✔ Secrets nunca en variables de entorno  

---

## 📞 Referencias

- Vault Documentation: https://developer.hashicorp.com/vault
- MCP Specification: https://modelcontextprotocol.io
- HMAC RFC: https://tools.ietf.org/html/rfc2104
