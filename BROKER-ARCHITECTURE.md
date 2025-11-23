# 📡 BROKER-ARCHITECTURE — SmarterOS Event Streaming (Redpanda)

## 🎯 Objetivo
Arquitectura de mensajería event-driven para auditoría, monitoreo y sincronización multi-tenant.

---

## 🧱 Componentes

```
┌─────────────────────────────────────────┐
│         SmarterOS Services              │
│  (API, Odoo, Shopify, Chatwoot, n8n)   │
└──────────────┬──────────────────────────┘
               │ Produce Events
               ▼
        ┌──────────────┐
        │   Redpanda   │  ← Kafka-compatible
        │   Cluster    │
        └──────────────┘
               │ Consume Events
               ▼
    ┌─────────────────────────┐
    │    Consumers            │
    │  • Audit Logger         │
    │  • Metabase Sync        │
    │  • Real-time Dashboard  │
    │  • Alerting System      │
    └─────────────────────────┘
```

---

## 📊 Topics por Tenant

### Nomenclatura
```
smarteros.{tenant_id}.{service}.{event_type}
```

### Ejemplos
```
smarteros.76953480-3.shopify.order_created
smarteros.76953480-3.odoo.sale_order_confirmed
smarteros.76953480-3.chatwoot.message_created
smarteros.76953480-3.n8n.workflow_completed
smarteros.76953480-3.botpress.handoff_triggered
```

---

## 🔄 Event Schema

### Base Event
```json
{
  "event_id": "uuid",
  "event_type": "order_created",
  "tenant_id": "76953480-3",
  "service": "shopify",
  "timestamp": "2025-11-23T12:00:00Z",
  "user_id": "user_abc",
  "data": {},
  "metadata": {
    "ip_address": "190.45.12.34",
    "user_agent": "Mozilla/5.0...",
    "trace_id": "trace_xyz"
  }
}
```

---

## 📦 Eventos por Servicio

### Shopify
```
smarteros.{tenant}.shopify.order_created
smarteros.{tenant}.shopify.order_updated
smarteros.{tenant}.shopify.order_cancelled
smarteros.{tenant}.shopify.product_created
smarteros.{tenant}.shopify.inventory_updated
```

**Payload Example:**
```json
{
  "event_type": "order_created",
  "tenant_id": "76953480-3",
  "service": "shopify",
  "data": {
    "order_id": 450789469,
    "order_number": "#1234",
    "total_price": "199990",
    "customer_email": "cliente@example.com",
    "line_items": [...]
  }
}
```

### Odoo
```
smarteros.{tenant}.odoo.sale_order_created
smarteros.{tenant}.odoo.sale_order_confirmed
smarteros.{tenant}.odoo.invoice_created
smarteros.{tenant}.odoo.payment_registered
smarteros.{tenant}.odoo.stock_updated
```

### Chatwoot
```
smarteros.{tenant}.chatwoot.conversation_created
smarteros.{tenant}.chatwoot.message_created
smarteros.{tenant}.chatwoot.agent_assigned
smarteros.{tenant}.chatwoot.conversation_resolved
```

**Payload Example:**
```json
{
  "event_type": "message_created",
  "tenant_id": "76953480-3",
  "service": "chatwoot",
  "data": {
    "conversation_id": 123,
    "message": "Necesito ayuda",
    "sender_type": "customer",
    "intent": "support",
    "confidence": 0.89
  }
}
```

### n8n
```
smarteros.{tenant}.n8n.workflow_started
smarteros.{tenant}.n8n.workflow_completed
smarteros.{tenant}.n8n.workflow_failed
smarteros.{tenant}.n8n.webhook_received
```

### Botpress
```
smarteros.{tenant}.botpress.agent_invoked
smarteros.{tenant}.botpress.handoff_triggered
smarteros.{tenant}.botpress.rag_query_executed
smarteros.{tenant}.botpress.intent_classified
```

---

## 🔐 Seguridad

### ACLs por Tenant
```yaml
# Redpanda ACL Configuration
acls:
  - principal: "User:tenant-76953480-3"
    resource: "Topic:smarteros.76953480-3.*"
    operations:
      - WRITE
      - READ
      - DESCRIBE

  - principal: "User:service-api-gateway"
    resource: "Topic:smarteros.*"
    operations:
      - WRITE
      - READ
      - DESCRIBE
```

### Authentication
```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='redpanda.smarterbot.cl:9092',
    security_protocol='SASL_SSL',
    sasl_mechanism='SCRAM-SHA-256',
    sasl_plain_username='service-api-gateway',
    sasl_plain_password=vault.read('secret/system/redpanda/password')
)
```

---

## 📤 Producer Implementation

### Python Producer
```python
import json
from kafka import KafkaProducer
from datetime import datetime

class SmarterosBroker:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.producer = KafkaProducer(
            bootstrap_servers='redpanda.smarterbot.cl:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def publish_event(self, service: str, event_type: str, data: dict):
        topic = f"smarteros.{self.tenant_id}.{service}.{event_type}"
        
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "tenant_id": self.tenant_id,
            "service": service,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        self.producer.send(topic, event)
        self.producer.flush()

# Usage
broker = SmarterosBroker(tenant_id="76953480-3")
broker.publish_event("shopify", "order_created", {
    "order_id": 450789469,
    "total_price": "199990"
})
```

---

## 📥 Consumer Implementation

### Audit Logger
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'smarteros.*.*.message_created',  # All message events
    bootstrap_servers='redpanda.smarterbot.cl:9092',
    group_id='audit-logger',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value
    
    # Save to audit log
    supabase.table('audit_logs').insert({
        'event_id': event['event_id'],
        'tenant_id': event['tenant_id'],
        'service': event['service'],
        'event_type': event['event_type'],
        'data': event['data'],
        'timestamp': event['timestamp']
    }).execute()
```

### Real-time Dashboard
```python
consumer = KafkaConsumer(
    'smarteros.*.shopify.order_created',
    bootstrap_servers='redpanda.smarterbot.cl:9092',
    group_id='dashboard-realtime'
)

for message in consumer:
    event = message.value
    
    # Update dashboard metrics
    redis.hincrby(f"metrics:{event['tenant_id']}", 'orders_today', 1)
    redis.incrby(f"revenue:{event['tenant_id']}", event['data']['total_price'])
    
    # Send WebSocket notification
    websocket.broadcast(event['tenant_id'], {
        'type': 'order_created',
        'data': event['data']
    })
```

---

## 📊 Consumer Groups

| Consumer Group        | Topics Subscribed                    | Purpose                  |
|-----------------------|--------------------------------------|--------------------------|
| audit-logger          | smarteros.*.*.*                      | Log all events           |
| metabase-sync         | smarteros.*.*.order_*                | Sync to analytics DB     |
| dashboard-realtime    | smarteros.*.*.order_created          | Update dashboard         |
| alerting-system       | smarteros.*.*.workflow_failed        | Send alerts              |
| email-notifications   | smarteros.*.odoo.invoice_created     | Send invoice emails      |
| whatsapp-bot          | smarteros.*.chatwoot.handoff_*       | Handle AI → human        |

---

## 📈 Monitoreo

### Redpanda Console
```yaml
# docker-compose.yml
services:
  redpanda-console:
    image: vectorized/console:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_BROKERS: redpanda:9092
```

### Metrics
- Messages per second per topic
- Consumer lag
- Disk usage per tenant
- Retention policy compliance

### Alertas
```yaml
# Alert: Consumer Lag > 1000
alert: HighConsumerLag
expr: kafka_consumer_lag > 1000
for: 5m
labels:
  severity: warning
annotations:
  summary: "Consumer {{ $labels.group }} is lagging"
```

---

## 🗑️ Retention Policy

### Per Topic
```
smarteros.*.*.order_* → 90 days
smarteros.*.*.message_* → 30 days
smarteros.*.*.workflow_* → 7 days
```

### Configuration
```bash
rpk topic alter-config smarteros.76953480-3.shopify.order_created \
  --set retention.ms=7776000000  # 90 days
```

---

## 🚀 Deployment

### Docker Compose
```yaml
services:
  redpanda:
    image: vectorized/redpanda:latest
    command:
      - redpanda
      - start
      - --smp 1
      - --memory 1G
      - --overprovisioned
      - --node-id 0
      - --kafka-addr PLAINTEXT://0.0.0.0:29092,EXTERNAL://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://redpanda:29092,EXTERNAL://redpanda.smarterbot.cl:9092
    ports:
      - "9092:9092"
      - "9644:9644"
    volumes:
      - redpanda_data:/var/lib/redpanda/data
```

---

## 🧪 Testing

### Produce Test Event
```bash
echo '{"test": "event"}' | rpk topic produce smarteros.76953480-3.test.event_test
```

### Consume Test Event
```bash
rpk topic consume smarteros.76953480-3.test.event_test
```

### List Topics
```bash
rpk topic list | grep "76953480-3"
```

---

## 🎯 Use Cases

### 1. Audit Completo
Todos los eventos se loguean para compliance.

### 2. Analytics Real-time
Metabase consume eventos y actualiza dashboards.

### 3. Sincronización Multi-Servicio
Orden Shopify → Event → n8n → Odoo → Chatwoot

### 4. Alertas Críticas
Workflow failed → Event → Alerting System → WhatsApp

### 5. Data Lake
Todos los eventos → S3 → Data warehouse

---

## 🚀 Roadmap

- ✅ Topics básicos
- ✅ Audit logger
- ⏳ Metabase real-time sync
- ⏳ Dead letter queue (DLQ)
- ⏳ Event replay
- ⏳ Schema registry
- ⏳ Multi-region replication
- ⏳ GDPR compliance (data deletion)
