# 🛍️ SHOPIFY-ODOO-SYNC — SmarterOS E-commerce Integration

## 🎯 Objetivo
Sincronización bidireccional automática entre tienda Shopify y ERP Odoo por tenant.

---

## 🔄 Flujo General

```
Shopify Store → Webhook → API Gateway → Supabase → Odoo
                  ↓
              Validation (HMAC)
                  ↓
              Tenant Routing (RUT)
                  ↓
              n8n Workflow (opcional)
```

---

## 📦 Webhooks Shopify

### Configuración
```json
{
  "topic": "orders/create",
  "address": "https://api.smarterbot.cl/shopify/webhook/orders",
  "format": "json"
}
```

### Topics Soportados
- `orders/create` - Nueva orden
- `orders/updated` - Actualización de orden
- `orders/cancelled` - Cancelación
- `products/create` - Nuevo producto
- `products/update` - Actualización de producto
- `inventory_levels/update` - Cambio de stock
- `customers/create` - Nuevo cliente

---

## 🔐 Validación HMAC

```python
import hmac
import hashlib
import base64

def verify_shopify_webhook(data: bytes, hmac_header: str, secret: str) -> bool:
    """Valida webhook de Shopify"""
    digest = hmac.new(
        secret.encode('utf-8'),
        data,
        hashlib.sha256
    ).digest()
    
    computed_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(computed_hmac, hmac_header)
```

---

## 📥 Ingreso a Supabase

### Tabla: `shopify_orders`
```sql
CREATE TABLE shopify_orders (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  shopify_order_id BIGINT NOT NULL,
  order_number TEXT,
  customer_email TEXT,
  total_price DECIMAL(10,2),
  currency TEXT DEFAULT 'CLP',
  financial_status TEXT,
  fulfillment_status TEXT,
  line_items JSONB,
  shipping_address JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  synced_to_odoo BOOLEAN DEFAULT FALSE,
  odoo_order_id INTEGER,
  UNIQUE(tenant_id, shopify_order_id)
);
```

### Inserción
```python
def save_shopify_order(tenant_id: str, order: dict):
    supabase.table('shopify_orders').insert({
        'tenant_id': tenant_id,
        'shopify_order_id': order['id'],
        'order_number': order['order_number'],
        'customer_email': order['email'],
        'total_price': order['total_price'],
        'currency': order['currency'],
        'financial_status': order['financial_status'],
        'fulfillment_status': order['fulfillment_status'],
        'line_items': order['line_items'],
        'shipping_address': order['shipping_address']
    }).execute()
```

---

## 🔄 Sync Inventario

### Shopify → Odoo
```python
def sync_inventory_to_odoo(tenant_id: str, product_sku: str, qty: int):
    # Get Odoo credentials from Vault
    odoo_creds = vault.read(f"secret/tenant/{tenant_id}/odoo")
    
    # Connect to Odoo
    odoo = OdooClient(
        url=odoo_creds['url'],
        db=odoo_creds['database'],
        username=odoo_creds['username'],
        password=odoo_creds['password']
    )
    
    # Find product by SKU
    product_id = odoo.search('product.product', [('default_code', '=', product_sku)])
    
    if product_id:
        # Update stock
        odoo.execute('stock.quant', 'update_quantity', {
            'product_id': product_id[0],
            'location_id': 8,  # Stock location
            'quantity': qty
        })
```

### Odoo → Shopify
```python
def sync_inventory_to_shopify(tenant_id: str, sku: str, qty: int):
    # Get Shopify credentials
    shopify_creds = vault.read(f"secret/tenant/{tenant_id}/shopify")
    
    # Update inventory
    response = requests.post(
        f"https://{shopify_creds['store_url']}/admin/api/2024-01/inventory_levels/set.json",
        headers={
            'X-Shopify-Access-Token': shopify_creds['api_key']
        },
        json={
            'location_id': shopify_creds['location_id'],
            'inventory_item_id': get_inventory_item_id(sku),
            'available': qty
        }
    )
```

---

## 📦 Sync Productos

### Estructura de Producto
```json
{
  "id": 7890,
  "title": "Taladro Black & Decker",
  "vendor": "Black & Decker",
  "product_type": "Herramientas",
  "variants": [
    {
      "id": 12345,
      "sku": "TD-BD-001",
      "price": "49990",
      "inventory_quantity": 15
    }
  ],
  "images": [
    {"src": "https://cdn.shopify.com/..."}
  ]
}
```

### Mapping Odoo
```python
FIELD_MAPPING = {
    'title': 'name',
    'vendor': 'manufacturer',
    'product_type': 'categ_id',
    'variants[0].sku': 'default_code',
    'variants[0].price': 'list_price',
    'variants[0].inventory_quantity': 'qty_available'
}
```

---

## 📝 Sync Órdenes

### Webhook Payload
```json
{
  "id": 450789469,
  "email": "cliente@example.com",
  "total_price": "199990",
  "currency": "CLP",
  "financial_status": "paid",
  "line_items": [
    {
      "id": 123,
      "title": "Taladro Black & Decker",
      "quantity": 2,
      "price": "49990",
      "sku": "TD-BD-001"
    }
  ],
  "shipping_address": {
    "first_name": "Juan",
    "last_name": "Pérez",
    "address1": "Los Pinos 123",
    "city": "Santiago",
    "province": "RM",
    "zip": "8320000"
  }
}
```

### Creación en Odoo
```python
def create_sale_order_from_shopify(tenant_id: str, shopify_order: dict):
    odoo = get_odoo_client(tenant_id)
    
    # Create or get partner
    partner_id = odoo.create_or_update_partner({
        'name': f"{shopify_order['shipping_address']['first_name']} {shopify_order['shipping_address']['last_name']}",
        'email': shopify_order['email'],
        'street': shopify_order['shipping_address']['address1'],
        'city': shopify_order['shipping_address']['city'],
        'zip': shopify_order['shipping_address']['zip']
    })
    
    # Create sale order
    order_lines = []
    for item in shopify_order['line_items']:
        product_id = odoo.search('product.product', [('default_code', '=', item['sku'])])
        if product_id:
            order_lines.append({
                'product_id': product_id[0],
                'product_uom_qty': item['quantity'],
                'price_unit': float(item['price'])
            })
    
    sale_order_id = odoo.create('sale.order', {
        'partner_id': partner_id,
        'order_line': [(0, 0, line) for line in order_lines],
        'client_order_ref': shopify_order['order_number'],
        'origin': f"Shopify #{shopify_order['order_number']}"
    })
    
    # Update Supabase
    supabase.table('shopify_orders').update({
        'synced_to_odoo': True,
        'odoo_order_id': sale_order_id
    }).eq('shopify_order_id', shopify_order['id']).execute()
    
    return sale_order_id
```

---

## 👥 Sync Clientes

### Shopify → Odoo Partner
```python
def sync_customer_to_odoo(tenant_id: str, customer: dict):
    odoo = get_odoo_client(tenant_id)
    
    partner_data = {
        'name': f"{customer['first_name']} {customer['last_name']}",
        'email': customer['email'],
        'phone': customer['phone'],
        'street': customer['default_address']['address1'],
        'city': customer['default_address']['city'],
        'zip': customer['default_address']['zip'],
        'customer_rank': 1,
        'comment': f"Shopify Customer ID: {customer['id']}"
    }
    
    # Check if exists
    existing = odoo.search('res.partner', [('email', '=', customer['email'])])
    
    if existing:
        odoo.write('res.partner', existing[0], partner_data)
    else:
        odoo.create('res.partner', partner_data)
```

---

## 🎯 Ejemplo E2E: Carrito Shopify → Odoo → WhatsApp

### Paso 1: Cliente compra en Shopify
```
Cliente agrega productos → Checkout → Pago (Webpay/Khipu)
```

### Paso 2: Webhook llega a API Gateway
```python
@app.post("/shopify/webhook/orders")
async def handle_shopify_order(request: Request):
    # Validate HMAC
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    body = await request.body()
    tenant_id = extract_tenant_from_store(request.headers.get('X-Shopify-Shop-Domain'))
    
    secret = vault.read(f"secret/tenant/{tenant_id}/shopify/webhook_secret")
    if not verify_shopify_webhook(body, hmac_header, secret):
        raise HTTPException(401, "Invalid HMAC")
    
    order = json.loads(body)
    
    # Save to Supabase
    save_shopify_order(tenant_id, order)
    
    # Create in Odoo
    odoo_order_id = create_sale_order_from_shopify(tenant_id, order)
    
    # Trigger n8n notification
    await trigger_n8n_workflow(tenant_id, "order_created", {
        "order_id": odoo_order_id,
        "customer_email": order['email'],
        "total": order['total_price']
    })
```

### Paso 3: n8n envía WhatsApp
```
n8n workflow → Chatwoot → WhatsApp:
"¡Hola Juan! Tu pedido #1234 por $199.990 fue confirmado.
Tracking: https://tienda.cl/track/ABC123"
```

---

## 📊 Monitoreo

### Métricas Clave
- Órdenes sincronizadas / hora
- Latencia Shopify → Odoo
- Errores de sync
- Productos sin SKU match
- Stock desincronizado

### Dashboard Metabase
```sql
SELECT 
  tenant_id,
  COUNT(*) as total_orders,
  SUM(CASE WHEN synced_to_odoo THEN 1 ELSE 0 END) as synced,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_sync_time
FROM shopify_orders
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY tenant_id;
```

---

## 🧪 Testing

### Mock Webhook
```bash
curl -X POST https://api.smarterbot.cl/shopify/webhook/orders \
  -H "X-Shopify-Hmac-Sha256: base64_hmac" \
  -H "X-Shopify-Shop-Domain: tienda.myshopify.com" \
  -d @test_order.json
```

### Validación Manual
```python
# Check sync status
order = supabase.table('shopify_orders').select('*').eq('shopify_order_id', 450789469).execute()
print(f"Synced to Odoo: {order['synced_to_odoo']}")
print(f"Odoo Order ID: {order['odoo_order_id']}")
```

---

## 🚀 Roadmap

- ✅ Sync órdenes básico
- ✅ Sync inventario
- ✅ Sync clientes
- ⏳ Sync tracking numbers (Odoo → Shopify)
- ⏳ Sync devoluciones
- ⏳ Sync descuentos y cupones
- ⏳ Multi-store por tenant
- ⏳ Sync en tiempo real (webhooks bidireccionales)
