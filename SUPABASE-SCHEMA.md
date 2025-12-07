# 🗄️ SUPABASE-SCHEMA — SmarterOS Database Model

## 🎯 Objetivo
Modelo de datos multi-tenant con Row-Level Security (RLS) para aislamiento por RUT.

---

## 📊 Tablas Principales

### `tenants`
```sql
CREATE TABLE tenants (
  id TEXT PRIMARY KEY,              -- RUT: 76953480-3
  rut TEXT UNIQUE NOT NULL,
  company_name TEXT NOT NULL,
  owner_user_id TEXT NOT NULL,
  
  -- Workspaces externos
  chatwoot_inbox_id INTEGER,
  botpress_workspace_id TEXT,
  n8n_default_workflow_id INTEGER,
  odoo_company_id INTEGER,
  vault_path TEXT,
  
  -- Configuración
  plan TEXT DEFAULT 'free',         -- free, starter, business, enterprise
  features JSONB DEFAULT '{}',
  settings JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP
);

-- Index
CREATE INDEX idx_tenants_rut ON tenants(rut);
CREATE INDEX idx_tenants_owner ON tenants(owner_user_id);
```

### `users`
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,              -- Clerk user_id
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  email TEXT NOT NULL,
  full_name TEXT,
  role TEXT DEFAULT 'member',       -- owner, admin, member, viewer
  
  -- External IDs
  odoo_user_id INTEGER,
  chatwoot_agent_id INTEGER,
  
  -- Metadata
  avatar_url TEXT,
  phone TEXT,
  metadata JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,
  
  UNIQUE(tenant_id, email)
);

-- RLS Policy
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_tenant_isolation ON users
  USING (tenant_id = current_setting('app.tenant_id')::TEXT);
```

### `shopify_orders`
```sql
CREATE TABLE shopify_orders (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  
  -- Shopify data
  shopify_order_id BIGINT NOT NULL,
  order_number TEXT,
  customer_email TEXT,
  customer_name TEXT,
  
  -- Financials
  total_price DECIMAL(12,2),
  currency TEXT DEFAULT 'CLP',
  financial_status TEXT,       -- paid, pending, refunded
  fulfillment_status TEXT,      -- fulfilled, partial, unfulfilled
  
  -- Items & Address
  line_items JSONB,
  shipping_address JSONB,
  billing_address JSONB,
  
  -- Sync status
  synced_to_odoo BOOLEAN DEFAULT FALSE,
  odoo_order_id INTEGER,
  sync_error TEXT,
  last_sync_at TIMESTAMP,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(tenant_id, shopify_order_id)
);

-- RLS Policy
ALTER TABLE shopify_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY shopify_orders_tenant_isolation ON shopify_orders
  USING (tenant_id = current_setting('app.tenant_id')::TEXT);

-- Index
CREATE INDEX idx_shopify_orders_tenant ON shopify_orders(tenant_id);
CREATE INDEX idx_shopify_orders_sync ON shopify_orders(synced_to_odoo);
```

### `products`
```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  
  -- Identity
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  
  -- Pricing
  price DECIMAL(12,2),
  currency TEXT DEFAULT 'CLP',
  cost DECIMAL(12,2),
  
  -- Inventory
  stock_quantity INTEGER DEFAULT 0,
  low_stock_threshold INTEGER DEFAULT 5,
  
  -- External IDs
  shopify_product_id BIGINT,
  shopify_variant_id BIGINT,
  odoo_product_id INTEGER,
  
  -- Metadata
  category TEXT,
  images JSONB,
  metadata JSONB DEFAULT '{}',
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(tenant_id, sku)
);

-- RLS Policy
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY products_tenant_isolation ON products
  USING (tenant_id = current_setting('app.tenant_id')::TEXT);
```

### `conversations`
```sql
CREATE TABLE conversations (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  
  -- Chatwoot data
  chatwoot_conversation_id INTEGER NOT NULL,
  inbox_id INTEGER,
  
  -- Participant
  customer_email TEXT,
  customer_phone TEXT,
  customer_name TEXT,
  
  -- Status
  status TEXT DEFAULT 'open',      -- open, resolved, pending
  assigned_agent_id TEXT REFERENCES users(id),
  
  -- AI Context
  intent TEXT,
  sentiment TEXT,
  handled_by_ai BOOLEAN DEFAULT FALSE,
  handoff_reason TEXT,
  
  -- Messages
  message_count INTEGER DEFAULT 0,
  last_message_at TIMESTAMP,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(tenant_id, chatwoot_conversation_id)
);

-- RLS Policy
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY conversations_tenant_isolation ON conversations
  USING (tenant_id = current_setting('app.tenant_id')::TEXT);
```

### `messages`
```sql
CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  conversation_id BIGINT NOT NULL REFERENCES conversations(id),
  
  -- Content
  content TEXT NOT NULL,
  message_type TEXT,               -- incoming, outgoing
  sender_type TEXT,                -- customer, agent, bot
  sender_id TEXT,
  
  -- AI Processing
  intent TEXT,
  entities JSONB,
  confidence DECIMAL(3,2),
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY messages_tenant_isolation ON messages
  USING (tenant_id = current_setting('app.tenant_id')::TEXT);

-- Index
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

### `knowledge_base`
```sql
CREATE TABLE knowledge_base (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  
  -- Document
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  content_type TEXT DEFAULT 'text',  -- text, pdf, image
  
  -- RAG
  embedding VECTOR(1536),            -- OpenAI ada-002
  chunk_index INTEGER,
  parent_document_id BIGINT,
  
  -- Metadata
  category TEXT,
  tags TEXT[],
  metadata JSONB DEFAULT '{}',
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

CREATE POLICY knowledge_base_tenant_isolation ON knowledge_base
  USING (tenant_id = current_setting('app.tenant_id')::TEXT);

-- Vector index (pgvector)
CREATE INDEX idx_kb_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
```

---

## 🔐 RLS Policies

### Global Policy Function
```sql
CREATE OR REPLACE FUNCTION get_tenant_id()
RETURNS TEXT AS $$
BEGIN
  RETURN current_setting('app.tenant_id', TRUE);
END;
$$ LANGUAGE plpgsql STABLE;
```

### Set Tenant Context
```python
# In API Gateway middleware
def set_tenant_context(tenant_id: str):
    supabase.rpc('set_config', {
        'setting_name': 'app.tenant_id',
        'setting_value': tenant_id,
        'is_local': True
    })
```

---

## 🔄 Clerk Webhook Mapping

### User Created
```sql
CREATE OR REPLACE FUNCTION handle_clerk_user_created()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO users (id, tenant_id, email, full_name)
  VALUES (
    NEW.clerk_user_id,
    NEW.tenant_id,
    NEW.email,
    NEW.full_name
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 📊 Vistas por Tenant

### Active Orders
```sql
CREATE VIEW v_active_orders AS
SELECT 
  o.id,
  o.order_number,
  o.customer_name,
  o.total_price,
  o.fulfillment_status,
  o.synced_to_odoo,
  t.company_name
FROM shopify_orders o
JOIN tenants t ON o.tenant_id = t.id
WHERE o.fulfillment_status != 'fulfilled'
  AND o.tenant_id = get_tenant_id();
```

### Sales Summary
```sql
CREATE VIEW v_sales_summary AS
SELECT 
  tenant_id,
  DATE_TRUNC('day', created_at) as date,
  COUNT(*) as order_count,
  SUM(total_price) as total_revenue,
  AVG(total_price) as avg_order_value
FROM shopify_orders
WHERE tenant_id = get_tenant_id()
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY tenant_id, DATE_TRUNC('day', created_at)
ORDER BY date DESC;
```

---

## 🧪 Testing

### Create Test Tenant
```sql
INSERT INTO tenants (id, rut, company_name, owner_user_id)
VALUES ('76953480-3', '76953480-3', 'Test Corp', 'user_test123');
```

### Set Context and Query
```sql
-- Set tenant context
SELECT set_config('app.tenant_id', '76953480-3', false);

-- Query with RLS
SELECT * FROM products;  -- Only returns tenant products
```

---

## 🚀 Migrations

### Run Migrations
```bash
supabase db push
supabase db remote commit
```

### Rollback
```bash
supabase db reset
```

---

## 📈 Performance

### Indexes Created
- Tenant ID on all tables
- Email lookups
- Order numbers
- Vector similarity (pgvector)
- Timestamp ranges

### Query Optimization
```sql
EXPLAIN ANALYZE 
SELECT * FROM shopify_orders 
WHERE tenant_id = '76953480-3' 
  AND created_at > NOW() - INTERVAL '7 days';
```
