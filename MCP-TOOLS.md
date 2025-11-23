# 🧠 MCP-TOOLS — SmarterOS Model Context Protocol

## 🎯 Objetivo
Catálogo completo de herramientas (tools) disponibles para agentes AI vía Model Context Protocol.

---

## 📦 Categorías de Tools

### 🔐 Authentication & Identity (3 tools)
### 🗄️ Tenant Management (5 tools)
### 🛍️ E-commerce (12 tools)
### 💬 Communication (8 tools)
### 📊 Analytics (6 tools)
### 🤖 AI & Automation (9 tools)

**Total: 43 tools**

---

## 🔐 Authentication & Identity

### `auth.validate_token`
Valida JWT de Clerk y extrae identidad.

**Input:**
```json
{
  "token": "eyJhbGc..."
}
```

**Output:**
```json
{
  "valid": true,
  "user_id": "user_abc",
  "tenant_id": "76953480-3",
  "email": "test@example.com"
}
```

### `auth.get_user_profile`
Obtiene perfil completo del usuario.

### `auth.refresh_token`
Refresca token expirado.

---

## 🗄️ Tenant Management

### `tenant.create`
Crea un nuevo tenant (onboarding).

**Input:**
```json
{
  "rut": "76953480-3",
  "company_name": "Ferretería Juanito",
  "owner_email": "owner@ferreteria.cl"
}
```

**Output:**
```json
{
  "tenant_id": "76953480-3",
  "chatwoot_inbox": 14,
  "botpress_workspace": "bp_123",
  "odoo_company_id": 3,
  "vault_path": "/secret/tenant/76953480-3/"
}
```

### `tenant.get`
Obtiene información de tenant.

### `tenant.update`
Actualiza configuración.

### `tenant.list_users`
Lista usuarios del tenant.

### `tenant.delete`
Elimina tenant (soft delete).

---

## 🛍️ E-commerce

### `shopify.get_products`
Lista productos de la tienda.

**Input:**
```json
{
  "tenant_id": "76953480-3",
  "limit": 50
}
```

### `shopify.get_product`
Detalle de un producto.

### `shopify.create_product`
Crea producto en Shopify.

### `shopify.update_inventory`
Actualiza stock.

### `shopify.get_orders`
Lista órdenes.

### `shopify.get_order`
Detalle de orden.

### `shopify.create_checkout`
Crea checkout asistido.

### `odoo.get_products`
Lista productos ERP.

### `odoo.create_sale_order`
Crea orden de venta en Odoo.

**Input:**
```json
{
  "tenant_id": "76953480-3",
  "customer_email": "cliente@example.com",
  "items": [
    {"sku": "TD-001", "quantity": 2}
  ]
}
```

### `odoo.get_inventory`
Consulta stock disponible.

### `odoo.sync_from_shopify`
Sincroniza orden Shopify → Odoo.

### `odoo.update_stock`
Actualiza inventario manualmente.

---

## 💬 Communication

### `chatwoot.send_message`
Envía mensaje a conversación.

**Input:**
```json
{
  "tenant_id": "76953480-3",
  "conversation_id": 123,
  "message": "Tu pedido está en camino",
  "message_type": "outgoing"
}
```

### `chatwoot.create_conversation`
Crea nueva conversación.

### `chatwoot.assign_agent`
Asigna agente humano.

### `chatwoot.handoff_to_human`
Deriva conversación de AI → humano.

**Input:**
```json
{
  "conversation_id": 123,
  "reason": "billing_sensitive",
  "context": {
    "last_intent": "refund_request",
    "customer_tier": "VIP"
  }
}
```

### `whatsapp.send_template`
Envía template pre-aprobado.

### `whatsapp.send_media`
Envía imagen/documento.

### `email.send`
Envía email transaccional.

### `sms.send`
Envía SMS (futuro).

---

## 📊 Analytics

### `analytics.get_sales`
Reporte de ventas.

**Input:**
```json
{
  "tenant_id": "76953480-3",
  "start_date": "2025-11-01",
  "end_date": "2025-11-23",
  "group_by": "day"
}
```

### `analytics.get_top_products`
Productos más vendidos.

### `analytics.get_customer_lifetime_value`
CLV por cliente.

### `analytics.get_conversion_rate`
Tasa de conversión.

### `analytics.get_abandoned_carts`
Carritos abandonados.

### `analytics.get_revenue_forecast`
Proyección de ingresos (ML).

---

## 🤖 AI & Automation

### `ai.classify_intent`
Clasifica intención de mensaje.

**Input:**
```json
{
  "message": "necesito una copia de mi factura",
  "context": {
    "tenant_id": "76953480-3",
    "customer_id": 456
  }
}
```

**Output:**
```json
{
  "intent": "invoice_request",
  "confidence": 0.95,
  "entities": {
    "document_type": "invoice"
  }
}
```

### `ai.ocr_document`
Extrae texto de imagen/PDF.

### `ai.rag_query`
Consulta base de conocimiento por tenant.

**Input:**
```json
{
  "tenant_id": "76953480-3",
  "query": "política de devoluciones",
  "top_k": 3
}
```

### `ai.generate_response`
Genera respuesta con LLM.

### `ai.summarize_conversation`
Resume conversación.

### `n8n.trigger_workflow`
Dispara workflow por ID.

**Input:**
```json
{
  "tenant_id": "76953480-3",
  "workflow_id": 431,
  "data": {
    "order_id": 789,
    "action": "notify_shipping"
  }
}
```

### `n8n.get_workflow_status`
Estado de ejecución.

### `n8n.list_workflows`
Lista workflows del tenant.

### `botpress.create_agent`
Crea agente especializado.

---

## 🛡️ Security & Rate Limits

### Per Tool
- Rate limit: 100 req/min por tenant
- Authentication: JWT + HMAC
- Audit: Todo llamado se loguea

### HMAC Signature
```python
def call_mcp_tool(tenant_id: str, tool_name: str, params: dict):
    # Get HMAC secret from Vault
    secret = vault.read(f"secret/tenant/{tenant_id}/mcp/hmac_key")
    
    # Sign request
    payload = json.dumps({"tool": tool_name, "params": params})
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    
    # Call API
    response = requests.post(
        "https://api.smarterbot.cl/mcp/tool",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "X-MCP-Signature": signature,
            "X-Tenant-ID": tenant_id
        },
        json={"tool": tool_name, "params": params}
    )
    
    return response.json()
```

---

## 🔌 Integración con Bolt Agents

### Ejemplo: Agent Order Checker
```typescript
// agents/order-checker.ts
import { MCPClient } from '@smarteros/mcp-sdk';

export async function checkOrder(orderId: string, tenantId: string) {
  const mcp = new MCPClient({ tenantId });
  
  // Get order from Odoo
  const order = await mcp.call('odoo.get_order', { order_id: orderId });
  
  // Get shipping status
  const shipping = await mcp.call('shopify.get_fulfillment', { order_id: order.shopify_id });
  
  // Generate response
  const response = await mcp.call('ai.generate_response', {
    template: 'order_status',
    data: { order, shipping }
  });
  
  return response;
}
```

---

## 📝 Tool Schema (OpenAPI)

```yaml
openapi: 3.0.0
info:
  title: SmarterOS MCP Tools
  version: 1.0.0

paths:
  /mcp/tool:
    post:
      summary: Execute MCP tool
      security:
        - BearerAuth: []
        - HMACAuth: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                tool:
                  type: string
                  example: "odoo.create_sale_order"
                params:
                  type: object
              required:
                - tool
                - params
```

---

## 🧪 Testing Tools

### Test Tool Call
```bash
curl -X POST https://api.smarterbot.cl/mcp/tool \
  -H "Authorization: Bearer ${JWT}" \
  -H "X-MCP-Signature: ${HMAC}" \
  -H "X-Tenant-ID: 76953480-3" \
  -d '{
    "tool": "ai.classify_intent",
    "params": {
      "message": "quiero devolver un producto"
    }
  }'
```

### Python SDK
```python
from smarteros_mcp import MCPClient

mcp = MCPClient(tenant_id="76953480-3", jwt=jwt_token)

# Classify intent
result = mcp.classify_intent("necesito ayuda con mi factura")
print(result)  # {'intent': 'invoice_support', 'confidence': 0.92}

# Create order
order_id = mcp.create_sale_order(
    customer_email="test@example.com",
    items=[{"sku": "TD-001", "quantity": 1}]
)
```

---

## 🚀 Roadmap

- ✅ 43 tools básicos
- ⏳ SDK Python/TypeScript
- ⏳ Bolt Agents integration
- ⏳ Tool chaining (pipelines)
- ⏳ Custom tools por tenant
- ⏳ Tool marketplace
- ⏳ Real-time tool execution monitoring
