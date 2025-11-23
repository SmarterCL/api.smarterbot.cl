# 📘 API-SPEC — SmarterOS API Gateway  
**Especificación técnica completa de endpoints, contratos y modelos**

## 🔐 Autenticación (Clerk SSO)

### `GET /auth/me`
Retorna el usuario autenticado.

**Headers**
- Authorization: Bearer {JWT}

**Response**
```json
{
  "id": "user_123",
  "email": "test@example.com",
  "tenant_id": "76953480-3"
}
```

### `POST /auth/validate`
Valida y refresca token Clerk.

**Body**
```json
{
  "token": "..."
}
```

---

## 🧠 AI Service

### `POST /ai/chat`
Chat multi-turno con contexto por tenant.

**Body**
```json
{
  "tenant_id": "76953480-3",
  "messages": [
    {"role": "user", "content": "hola"}
  ]
}
```

### `POST /ai/rag/query`
Consulta RAG por tenant.

**Body**
```json
{
  "tenant_id": "76953480-3",
  "query": "política de devoluciones"
}
```

### `POST /ai/ocr`
OCR + clasificación LLM.

---

## 🛍️ Shopify

### `POST /shopify/webhook/orders`
Webhook ordenes.

### `POST /shopify/webhook/products`
Sync catálogo.

---

## 📦 Odoo ERP

### `GET /odoo/products`
Lista de productos por tenant.

### `POST /odoo/orders`
Crea una orden de venta.

---

## 💬 Chatwoot

### `POST /chatwoot/webhook`
Eventos entrantes desde WhatsApp/Email/Web.

### `POST /chatwoot/send`
Enviar mensaje desde API.

---

## 🤖 n8n

### `POST /n8n/trigger`
Disparar workflows.

---

## 🗂️ Modelos Clave

### Tenant
```json
{
  "id": "76953480-3",
  "workspace_id": "bp_123",
  "chatwoot_id": 14,
  "vault_secrets": "/secret/tenant/76953480-3/"
}
```

---

## 🔒 Seguridad

- Clerk JWT
- HMAC Shopify
- RLS en Supabase
- Vault secrets por tenant
- Rate-limits

---

## 🧪 Testing

- Pytest
- Mock Shopify / Odoo
- Test multi-tenant
