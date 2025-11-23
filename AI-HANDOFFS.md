# 🤖🧑 AI-HANDOFFS — SmarterOS Cognitive Architecture

## 🎯 Objetivo
Permitir que agentes AI (Botpress) deriven automáticamente conversaciones a humanos (Chatwoot).

---

## 🔄 Flujo General

```
User → Chatwoot → Botpress → (AI decisión)
                    ↳ Respuesta automática
                    ↳ Handoff → Chatwoot human
```

---

## 🧠 Detección de intención
Botpress identifica:
- Soporte técnico  
- Preguntas de ventas  
- Reclamos  
- Facturación  
- Información general  

---

## 🧭 Reglas de Handoff
- Baja confianza del LLM  
- Categoría sensible  
- Cliente VIP  
- Demora > 5s  
- Fin de workflow  

---

## ✉️ Payload enviado a Chatwoot
```json
{
  "event": "handoff",
  "to": "human",
  "reason": "billing_sensitive"
}
```

---

## 📡 Endpoint Gateway
```
POST /chatwoot/send
```

---

## 📝 Logs
Todos los handoffs quedan registrados como:

- timestamp
- tenant
- intent
- agent
- decisión
