# 🗂️ TENANT-MODEL — Multi-Tenant SmarterOS

## 🎯 Concepto Principal
Cada empresa chilena = **1 tenant**  
Cada tenant = **1 RUT**  
Cada RUT = **un workspace aislado**

---

## 🧱 Estructura del Tenant
```json
{
  "tenant_id": "76953480-3",
  "rut": "76953480-3",
  "company_name": "Ferretería Juanito",
  "owner_user_id": "user_abc",
  "chatwoot_inbox": 14,
  "botpress_workspace": "bp_123",
  "n8n_default_workflow": 431,
  "odoo_company_id": 3,
  "vault_path": "/secret/tenant/76953480-3/",
  "created_at": "2025-11-23T10:32:00Z"
}
```

---

## 🔐 Aislamiento por Tenant

- RLS en Supabase
- Secretos en Vault
- Workspaces Botpress aislados
- Inboxes Chatwoot independientes
- Flujos n8n por empresa

---

## 📦 Recursos por Tenant

| Servicio   | Aislamiento     | Implementación    |
|------------|-----------------|-------------------|
| Chatwoot   | Inbox           | API Gateway       |
| Botpress   | Workspace       | API Gateway       |
| n8n        | Workflow        | Trigger ID        |
| Odoo       | Company         | auth_clerk addon  |
| Supabase   | RLS             | Policies por rut  |
| Vault      | Path            | /tenant/{rut}     |

---

## 🚀 Proceso de Creación (Onboarding)

1. Usuario inicia sesión via Clerk
2. API valida el RUT
3. Se crea tenant en Supabase
4. Se crean recursos:
   - Chatwoot inbox
   - Botpress workspace
   - Carpeta Vault
   - Company Odoo
   - Workflow inicial n8n
5. Portal redirige a dashboard

---

## 📊 Indexación RAG
Los documentos se guardan como:
```
storage/tenant/{rut}/kb/*
embeddings/tenant/{rut}
```

---

## 🧪 Testing

- Crear tenant
- Aislamiento de datos
- Workflows n8n independientes
