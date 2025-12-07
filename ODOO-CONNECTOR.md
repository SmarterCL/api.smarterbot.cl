# 🔌 ODOO-CONNECTOR — SmarterOS ERP Integration

## 🎯 Objetivo
Unificar usuarios, productos, órdenes y pagos entre SmarterOS → Odoo 19.0

---

## 🔐 Autenticación SSO
El addon `auth_clerk` permite:

- Login sin contraseña  
- Crear usuarios automáticamente  
- Asociar tenant → odoo_company_id  
- Control de permisos

---

## 🛍️ Productos

### Sync Odoo → SmarterOS
- ID
- Nombre
- SKU
- Precio
- Stock
- Categorías

---

## 📝 Ordenes de Venta

### `POST /odoo/orders`
```json
{
  "tenant_id": "76953480-3",
  "customer": {"name": "Pedro"},
  "items": [{"product_id": 44, "qty": 1}]
}
```

Crea:
- partner
- sale.order
- sale.order.line

---

## 🔄 Webhooks

- Actualización de stock
- Estado de órdenes
- Notificaciones a CRM

---

## 🧱 Arquitectura

```
API Gateway → Odoo XML-RPC/JSON-RPC → Odoo Models
```

---

## 🧪 Tests

- Creación de usuario
- Sync de productos
- Creación de orden
