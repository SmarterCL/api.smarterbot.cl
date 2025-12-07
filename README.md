# SmarterOS API - Enterprise API with MCP Integration

**La API central de SmarterOS**: Plataforma gobernada con FastAPI-MCP, Qwen LLM y OpenRouter para empresas chilenas.

[![API Status](https://img.shields.io/badge/status-production-brightgreen)](https://api.smarterbot.cl/health)
[![Governed Mode](https://img.shields.io/badge/mode-governed-blue)](https://api.smarterbot.cl/)
[![MCP Enabled](https://img.shields.io/badge/MCP-enabled-purple)](https://api.smarterbot.cl/mcp)

---

## 🌐 URLs de Producción

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API Principal** | https://api.smarterbot.cl | Endpoint principal |
| **API Alternativa** | https://api.smarterbot.store | Mirror endpoint |
| **Documentación** | https://api.smarterbot.cl/docs | OpenAPI Swagger UI |
| **Health Check** | https://api.smarterbot.cl/health | Estado del sistema |

---

## 🚀 ¿Qué es SmarterOS?

**SmarterOS** es un sistema operativo empresarial de código abierto, autoalojado en contenedores, que permite implementar en tiempo récord una PyME o Empresa con:

- ✅ **Inteligencia Artificial** (Qwen LLM + OpenRouter)
- ✅ **Contabilidad Automática** (Odoo ERP)
- ✅ **Pagos para Chile** (Flow, Mercado Pago)
- ✅ **Cumplimiento SII** (Validación tributaria en línea)
- ✅ **Operación 24/7** (Sin personal dedicado)

### 🇨🇱 Diseñado para Chile

Opera bajo **RUT empresa** con validación tributaria y cumplimiento automático con el **SII** (Servicio de Impuestos Internos), manteniendo la normativa actualizada en tiempo real.

### En términos simples

> **SmarterOS convierte tu empresa en un sistema automático, inteligente y legalmente válido para operar en Chile.**

---

## 🎯 Esta API

Esta API es el **cerebro central** de SmarterOS, construida con:

- **FastAPI**: Framework Python moderno y rápido
- **FastAPI-MCP v0.4.0**: Integración nativa del Model Context Protocol
- **Qwen (Alibaba Cloud)**: LLM enterprise principal
- **OpenRouter**: Fallback multi-modelo (GPT-4, Claude, etc.)
- **Modo Governed**: Validación y trazabilidad automática

### ✨ Características Únicas

- 🔄 **Auto-conversión** de endpoints FastAPI a MCP tools
- 🔐 **Autenticación nativa** con FastAPI Depends
- 📚 **Documentación automática** (OpenAPI/Swagger)
- 🚀 **ASGI transport** eficiente (sin overhead HTTP)
- 🎭 **Compatible** con Claude Desktop y agentes MCP
- 🛡️ **Modo governed** para auditoría continua

---

## 📡 Endpoints Disponibles

### Públicos (sin auth)

| Endpoint | Descripción | Ejemplo |
|----------|-------------|---------|
| `GET /` | Metadata de la API | [Ver](https://api.smarterbot.cl/) |
| `GET /health` | Estado del sistema | [Ver](https://api.smarterbot.cl/health) |
| `GET /docs` | Documentación interactiva | [Ver](https://api.smarterbot.cl/docs) |
| `GET /openapi.json` | Schema OpenAPI | [Ver](https://api.smarterbot.cl/openapi.json) |

### Protegidos (requieren auth)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/ai/qwen` | POST | Completions con Qwen (Alibaba Cloud) |
| `/ai/openrouter` | POST | Completions con OpenRouter (multi-modelo) |
| `/mcp` | POST | Model Context Protocol endpoint |

---

## 🔐 Autenticación

Los endpoints protegidos requieren un header de autorización:

```bash
Authorization: Bearer YOUR_API_TOKEN
```

---

## 🧪 Ejemplos de Uso

### 1. Metadata de la API

```bash
curl https://api.smarterbot.cl/
```

**Respuesta**:
```json
{
  "name": "SmarterOS API MCP",
  "version": "2.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/health",
  "mcp": "/mcp",
  "openapi": "/openapi.json",
  "governed": true,
  "endpoints": {
    "qwen": "/ai/qwen",
    "openrouter": "/ai/openrouter"
  }
}
```

### 2. Health Check

```bash
curl https://api.smarterbot.cl/health
```

**Respuesta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-07T16:21:00Z",
  "mcp_enabled": true,
  "mcp_mode": "governed",
  "qwen_configured": true,
  "openrouter_configured": true
}
```

### 3. Qwen Completion

```bash
curl -X POST https://api.smarterbot.cl/ai/qwen \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Qué es SmarterOS y cómo ayuda a las PyMEs chilenas?",
    "model": "qwen-turbo"
  }'
```

### 4. OpenRouter Completion (GPT-4, Claude, etc.)

```bash
curl -X POST https://api.smarterbot.cl/ai/openrouter \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Necesito ayuda con facturación electrónica en Chile",
    "model": "openai/gpt-4"
  }'
```

### 5. MCP Protocol

```bash
curl -X POST https://api.smarterbot.cl/mcp \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

---

## 🛠️ Instalación Local

### Requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.12+ (para desarrollo)

### Quick Start

```bash
# 1. Clonar el repositorio
git clone https://github.com/SmarterCL/api.smarterbot.cl
cd api.smarterbot.cl

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 3. Iniciar con Docker Compose
docker-compose up -d

# 4. Verificar
curl http://localhost:3002/health | jq
```

### Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 3000

# Ver en navegador
open http://localhost:3000/docs
```

---

## 📦 Stack Tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **FastAPI** | 0.124.0+ | Framework web ASGI |
| **FastAPI-MCP** | 0.4.0 | Integración MCP |
| **Pydantic** | 2.10.0+ | Validación de datos |
| **Uvicorn** | 0.32.0+ | Servidor ASGI |
| **httpx** | 0.27.0+ | Cliente HTTP async |
| **Docker** | 20.10+ | Containerización |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              Internet (HTTPS)                        │
└───────────────────┬─────────────────────────────────┘
                    │
            ┌───────▼────────┐
            │  Caddy Proxy   │ (SSL/TLS)
            │  Port 443      │
            └───────┬────────┘
                    │
        ┌───────────▼──────────────┐
        │   smarteros-api-mcp      │
        │   FastAPI + MCP          │
        │   Port 3002:3000         │
        │   ├─ Qwen API            │
        │   ├─ OpenRouter API      │
        │   ├─ MCP Tools           │
        │   └─ Governed Mode       │
        └──────────────────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
┌───────▼────────┐     ┌──────────▼─────────┐
│ Qwen API       │     │ OpenRouter API     │
│ (Alibaba)      │     │ (Multi-modelo)     │
└────────────────┘     └────────────────────┘
```

---

## 🚀 Despliegue

### Producción Actual

- **Servidor**: VPS con Docker Swarm
- **Proxy**: Caddy (auto SSL/TLS)
- **Network**: `smarteros` (Docker network)
- **Restart Policy**: `unless-stopped`
- **Health Checks**: Activos cada 30s

### CI/CD (Recomendado)

```yaml
# .github/workflows/deploy.yml
name: Deploy API
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Deploy
        run: |
          docker-compose build
          docker-compose up -d
```

---

## 📚 Documentación Adicional

### En este repositorio

- `API-SPEC.md` - Especificaciones técnicas
- `MCP-TOOLS.md` - Documentación de MCP tools
- `BROKER-ARCHITECTURE.md` - Arquitectura del broker
- `SUPABASE-SCHEMA.md` - Schema de base de datos
- `VAULT-POLICY.md` - Políticas de Vault

### Enlaces externos

- **SmarterOS Org**: https://github.com/SmarterCL
- **FastAPI-MCP**: https://github.com/tadata-org/fastapi_mcp
- **OpenAPI Docs**: https://api.smarterbot.cl/docs
- **ReDoc**: https://api.smarterbot.cl/redoc

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Guías de contribución

- Sigue el estilo de código existente
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación
- Asegúrate de que todos los tests pasen

---

## 🐛 Reportar Issues

Si encuentras un bug o tienes una sugerencia:

1. Ve a [Issues](https://github.com/SmarterCL/api.smarterbot.cl/issues)
2. Busca si ya existe un issue similar
3. Si no existe, crea uno nuevo con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica

---

## 📝 Licencia

Este proyecto es parte de **SmarterOS** y se distribuye bajo licencia de código abierto.

Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto y Soporte

### Email
- **Soporte**: smarterbotcl@gmail.com
- **Consultas comerciales**: smarterbotcl@gmail.com

### GitHub
- **Issues**: https://github.com/SmarterCL/api.smarterbot.cl/issues
- **Discussions**: https://github.com/SmarterCL/api.smarterbot.cl/discussions

### Comunidad
- **GitHub Org**: https://github.com/SmarterCL
- **Website**: https://smarteros.cl (próximamente)

---

## 🎯 Roadmap

### ✅ Completado
- [x] API base con FastAPI
- [x] Integración FastAPI-MCP
- [x] Qwen LLM integration
- [x] OpenRouter fallback
- [x] Modo governed
- [x] Documentación OpenAPI
- [x] Health checks
- [x] Root endpoint informativo
- [x] Docker containerization
- [x] Producción activa

### 🚧 En Progreso
- [ ] Rate limiting por tenant
- [ ] Metrics endpoint (Prometheus)
- [ ] OpenSpec contract validation
- [ ] Webhook notifications

### 📋 Próximamente
- [ ] Multi-tenant support
- [ ] Usage tracking dashboard
- [ ] Custom MCP tools registry
- [ ] GitHub Actions CI/CD
- [ ] API key management
- [ ] Billing integration

---

## ⭐ Agradecimientos

- **FastAPI-MCP** por la increíble integración MCP
- **Alibaba Cloud** por Qwen LLM
- **OpenRouter** por el acceso multi-modelo
- **Comunidad FastAPI** por el framework

---

## 🏆 Stats

![GitHub stars](https://img.shields.io/github/stars/SmarterCL/api.smarterbot.cl?style=social)
![GitHub forks](https://img.shields.io/github/forks/SmarterCL/api.smarterbot.cl?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/SmarterCL/api.smarterbot.cl?style=social)

---

<div align="center">

**Hecho con ❤️ por el equipo de SmarterOS**

[Website](https://smarteros.cl) • [GitHub](https://github.com/SmarterCL) • [Docs](https://api.smarterbot.cl/docs)

</div>
