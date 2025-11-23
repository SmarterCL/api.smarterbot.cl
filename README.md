# 🚀 SmarterOS API Gateway  
**Centro neural del Operating System multi-tenant para PYMEs de Chile**

La API Gateway es el **cerebro central** que conecta toda la arquitectura de SmarterOS:  
ERP, CRM, Chat, Automatizaciones, Bots IA, Seguridad, y los módulos cognitivos multi-tenant por RUT.

Sirve como:
- 🔐 Proveedor de seguridad (SSO + JWT + RUT)
- 🧠 Router inteligente multi-servicio
- 🔌 Integrador entre sistemas externos (Shopify, Odoo, Botpress, n8n)
- 🗂️ Normalizador de datos multi-tenant
- 🛡️ Capa de gobernanza y auditoría (MCP + Vault)

---

# 🧩 **Funciones Críticas**

## 1. 🔐 **Autenticación Unificada (SSO Clerk)**
- Valida JWT emitidos por Clerk  
- Extrae `user_id`, `email`, `rut`, `tenant_id`  
- Crea automáticamente usuarios en Supabase y Odoo  
- Renovación de tokens en background  
- Middleware universal para todos los endpoints  

---

## 2. 🗄️ **Gestión Multi-Tenant por RUT**
Basado en:

- Tenant = RUT chileno
- API Gateway asigna contexto  
- Todas las consultas/mensajes/automatizaciones usan este tenant

Implementación:
- Row-Level Security en Supabase  
- Secrets aislados en Vault  
- Workspaces separados en Botpress, Chatwoot y n8n  
- Catalogación de productos por tenant (Shopify/Odoo)  
- Logs por tenant en Redpanda (próxima fase)

---

## 3. 🤖 **Orquestación AI + MCP**
La API provee una capa de orquestación AI con:

- OpenAI GPT-4.1 / GPT-4.1 Turbo  
- Claude 3.5 Sonnet / Haiku  
- Gemini 2.0 Pro  
- Model Context Protocol (MCP)  
- RAG con pgvector por tenant  
- Handlers para:
  - Preguntas frecuentes
  - Embeddings
  - OCR
  - Clasificación LLM
  - Carritos eCommerce automáticos

---

## 4. 🔌 **Integración con Plataformas**

### Shopify
- Webhooks verificados por HMAC  
- Carritos asistidos  
- Import/export productos  
- Inventario → Odoo  
- Checkout inteligente  

### Odoo
- Login SSO  
- Creación automática de usuarios  
- Catálogo e inventario  
- Órdenes de venta  
- Actualización de stock  
- Conector multi-tenant  

### Chatwoot (CRM Inbox)
- Creación de conversaciones  
- Derivaciones a agentes  
- Respuestas con IA  
- Activación de flujos n8n  

### n8n (Automatizaciones)
- Activación de workflows  
- Lectura/escritura de datos  
- Notificaciones y webhooks  
- OCR → clasificación → respuesta  

### Botpress (Agentes de IA)
- Multi-agent  
- Contexto persistente  
- Hand-offs inteligentes  
- Acceso seguro vía Gateway  

---

# 🧱 **Arquitectura**

```
      [ User ]
         |
    (Clerk Login)
         |
   ┌───────────────┐
   │  API Gateway  │  ← FastAPI + Clerk + Supabase + MCP
   └───────────────┘
 /     |       |       \
/      |       |        \
[Odoo] [Chatwoot] [n8n] [Botpress]
  |        |        |        |
(ERP)   (Inbox) (Automation) (AI Agents)

  + KPI (Metabase)
  + Storage (Supabase)
  + Secrets (Vault)
```

---

# 📡 **Principales Endpoints**

## 🔐 Auth

```
GET  /auth/me
POST /auth/validate
POST /auth/refresh
```

## 🧠 AI

```
POST /ai/chat
POST /ai/rag/query
POST /ai/classify
POST /ai/ocr
```

## 🛍️ Shopify / Odoo

```
POST /shopify/webhook/orders
POST /shopify/webhook/products
GET  /odoo/products
POST /odoo/orders
```

## 💬 Chatwoot

```
POST /chatwoot/webhook
POST /chatwoot/send
```

## 🤖 Automatizaciones n8n

```
POST /n8n/trigger
POST /n8n/workflow/{id}
```

---

# 🛡️ **Seguridad Multi-Capa**

✔ Clerk JWT Validation  
✔ HMAC Shopify  
✔ Supabase RLS  
✔ Vault Secrets por tenant  
✔ Audit Logs (MCP)  
✔ Rate-limiting por IP  
✔ API Keys por integraciones  

---

# 📂 **Estructura del Repositorio**

```
/api
├─ app/
│  ├─ main.py
│  ├─ auth/
│  ├─ tenants/
│  ├─ shopify/
│  ├─ odoo/
│  ├─ chatwoot/
│  ├─ n8n/
│  └─ ai/
├─ tests/
├─ docker-compose.yml
├─ Dockerfile
└─ README.md  ← este documento
```

---

# 🔧 **Requisitos Técnicos**

- Docker 24+
- Python 3.11+
- FastAPI
- Clerk SDK
- Supabase Python SDK
- Pydantic v2
- PostgreSQL 16
- Redis (opcional)

---

# 🚀 **Deployment**

```bash
git pull origin main
docker compose build
docker compose up -d
```

Variables necesarias en `.env`:

```env
CLERK_SECRET_KEY=
CLERK_PUBLISHABLE_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

---

# 🗺️ **Roadmap 2026**

- 🔄 Sincronización Shopify/Odoo 2.0
- 🧾 Módulo de facturación SII
- 💳 Pagos Chile (Webpay, Khipu, MACH)
- 🧠 Agentes Cognitivos RUT → SII
- 📊 Analytics predictivo Next-Level
- 🧩 Shopify App pública
- 📱 App móvil SmarterOS

---

# 🤝 **Contacto**

**SmarterBot Chile — Plataforma Cognitiva para PYMEs**

🌍 https://smarterbot.cl  
✉️ smarterbotcl@gmail.com  
📱 +56 9 7954 0471  

---

**Hecho en Chile 🇨🇱**
