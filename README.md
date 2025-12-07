# API SmarterBot - Enterprise API with MCP Integration

**SmarterOS API** es la API empresarial de SmarterOS con integración nativa de FastAPI-MCP, Qwen LLM y OpenRouter.

---

## 🌐 URLs

- **Producción**: https://api.smarterbot.cl
- **Alternativa**: https://api.smarterbot.store
- **Documentación**: https://api.smarterbot.cl/docs

---

## 🚀 Sobre SmarterOS

**SmarterOS** es un sistema operativo de código abierto, autoalojado en contenedores, que permite implementar en tiempo récord una PyME o Empresa con inteligencia artificial, contabilidad y pagos para Chile.

Está diseñado para operar bajo RUT empresa, con validación tributaria y cumplimiento automático con el SII (Servicio de Impuestos Internos), manteniendo la normativa actualizada en tiempo real.

### Estructura del Repositorio

- **guias/**: Documentación, especificaciones y manuales
  - **guias/especificaciones/**: Especificaciones técnicas
  - **guias/guia-usuario/**: Guías de uso
- **servicios/**: Definiciones de servicios por dominio (API, App, ERP, CRM)
- **nucleo/**: Corazón del sistema (Agentes y Flujos de negocio)
- **infraestructura/**: Definiciones de infraestructura y flujos CI/CD
- **mcp/**: Protocolo de Contexto de Modelos (Specs)

### Qué permite hacer SmarterOS

- ✅ Crear una empresa digital operativa en horas, no en meses
- ✅ Automatizar ventas, pagos, facturación y soporte
- ✅ Cumplir automáticamente con normativa chilena
- ✅ Operar con IA sin perder control legal ni contable
- ✅ Escalar sin rehacer sistemas

### Capacidades Clave (Product Requirements)

- ✅ Autoalojado vía contenedores (Docker)
- ✅ Código abierto
- ✅ Multiempresa por RUT
- ✅ Validación tributaria en línea
- ✅ Integración con SII
- ✅ Motor contable automático
- ✅ Motor de pagos para Chile
- ✅ Automatización de procesos con IA
- ✅ Cumplimiento MCP para control y auditoría
- ✅ Operación 24/7 sin personal dedicado

### En términos simples

> **SmarterOS convierte una empresa en un sistema automático, inteligente y legalmente válido en Chile.**

---

## 🎯 Características de esta API

### FastAPI-MCP Integration

Esta API utiliza [FastAPI-MCP](https://github.com/tadata-org/fastapi_mcp) para exponer automáticamente los endpoints FastAPI como herramientas MCP (Model Context Protocol).

**Beneficios**:
- 🔄 Auto-conversión de endpoints a MCP tools
- 🔐 Autenticación nativa con FastAPI
- 📚 Documentación automática (OpenAPI/Swagger)
- 🚀 Transport ASGI eficiente
- 🎭 Compatible con Claude Desktop y agentes MCP

### LLM Integration

- **Qwen (Alibaba Cloud)**: LLM enterprise principal
- **OpenRouter**: Fallback multi-modelo
- **Modo Governed**: Validación y trazabilidad automática

---

## 📡 Endpoints

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check y estado del sistema |
| `/ai/qwen` | POST | Sí | Completions con Qwen (Alibaba) |
| `/ai/openrouter` | POST | Sí | Completions con OpenRouter |
| `/mcp` | POST | Sí | MCP protocol endpoint |
| `/docs` | GET | No | Documentación interactiva (Swagger) |

---

## 🔐 Autenticación

Todos los endpoints protegidos requieren:

```
Header: Authorization: Bearer <your-token>
```

---

## 🧪 Uso

### Health Check

```bash
curl https://api.smarterbot.cl/health
```

**Respuesta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-07T13:34:58Z",
  "mcp_enabled": true,
  "mcp_mode": "governed",
  "qwen_configured": true,
  "openrouter_configured": true
}
```

### Qwen Completion

```bash
curl -X POST https://api.smarterbot.cl/ai/qwen \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explica qué es SmarterOS",
    "model": "qwen-turbo"
  }'
```

### OpenRouter Completion

```bash
curl -X POST https://api.smarterbot.cl/ai/openrouter \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hola, necesito ayuda con mi empresa",
    "model": "openai/gpt-4"
  }'
```

### MCP Protocol

```bash
curl -X POST https://api.smarterbot.cl/mcp \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

---

## 🛠️ Despliegue Local

### Requisitos

- Docker & Docker Compose
- Python 3.12+
- Variables de entorno configuradas

### Quick Start

```bash
# Clonar repositorio
git clone https://github.com/SmarterCL/api.smarterbot.cl
cd api.smarterbot.cl

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus tokens

# Construir e iniciar
docker-compose up -d

# Verificar
curl http://localhost:3000/health
```

### Desarrollo

```bash
# Instalar dependencias
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar en desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

---

## 📦 Stack Tecnológico

- **FastAPI**: Framework web moderno y rápido
- **FastAPI-MCP**: Integración MCP nativa
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI
- **httpx**: Cliente HTTP asíncrono
- **Docker**: Containerización

---

## 🔄 CI/CD

Esta API se despliega automáticamente en:
- **Producción**: https://api.smarterbot.cl
- **Container**: `smarteros-api-mcp`
- **Network**: `smarteros` (Docker)
- **Proxy**: Caddy reverse proxy

---

## 📚 Documentación

- **OpenAPI Docs**: https://api.smarterbot.cl/docs
- **ReDoc**: https://api.smarterbot.cl/redoc
- **FastAPI-MCP**: https://github.com/tadata-org/fastapi_mcp
- **SmarterOS**: https://github.com/SmarterCL

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es parte de SmarterOS y se distribuye bajo licencia de código abierto.

---

## 🔗 Enlaces

- **SmarterOS**: https://smarteros.cl
- **GitHub Org**: https://github.com/SmarterCL
- **API Docs**: https://api.smarterbot.cl/docs

---

## 📞 Soporte

Para soporte y consultas:
- **Email**: smarterbotcl@gmail.com
- **GitHub Issues**: https://github.com/SmarterCL/api.smarterbot.cl/issues

---

**Hecho con ❤️ por el equipo de SmarterOS**
