import os
import time
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import httpx

# Import routers
from routers import runtime

# Rate Limiting Config (desde env o default)
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "300"))

# Tokens desde environment
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MCP_MODE = os.getenv("MCP_MODE", "governed")

# Almacenamiento en memoria para rate limiting
_tenant_counters = {}

app = FastAPI(
    title="SmarterOS API with MCP",
    description="Enterprise API with FastAPI-MCP integration and rate limiting",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
def get_tenant_from_token(auth_header: str):
    """Extract tenant/RUT from Authorization header"""
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    # Simple extraction: use token as tenant ID
    # En producción real, decodificar JWT y extraer RUT
    token = auth_header.replace("Bearer ", "")
    return token[:20]  # Primeros 20 chars como tenant ID

@app.middleware("http")
async def tenant_rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware por tenant"""
    
    # Rutas públicas sin límite
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    auth = request.headers.get("Authorization")
    tenant = get_tenant_from_token(auth)
    
    # Si no hay tenant (sin auth), no aplicar rate limit
    if not tenant:
        return await call_next(request)
    
    # Ventana de 1 minuto
    now_window = int(time.time() // 60)
    key = f"{tenant}:{now_window}"
    
    count = _tenant_counters.get(key, 0)
    
    if count >= RATE_LIMIT_RPM:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for tenant. Limit: {RATE_LIMIT_RPM} requests/minute",
            headers={"X-RateLimit-Limit": str(RATE_LIMIT_RPM), "X-RateLimit-Remaining": "0"}
        )
    
    _tenant_counters[key] = count + 1
    
    # Limpieza de ventanas antiguas
    old_keys = [k for k in _tenant_counters.keys() if not k.endswith(str(now_window))]
    for k in old_keys:
        _tenant_counters.pop(k, None)
    
    # Agregar headers de rate limit a la respuesta
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_RPM)
    response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT_RPM - count - 1)
    response.headers["X-RateLimit-Reset"] = str((now_window + 1) * 60)
    
    return response

# Auth dependency
async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    return authorization

# Models
class CompletionRequest(BaseModel):
    prompt: str
    model: str = "qwen-turbo"
    
class CompletionResponse(BaseModel):
    success: bool
    governed: bool
    timestamp: str
    result: dict

# Root endpoint
@app.get("/")
def root():
    """API root with metadata"""
    return {
        "name": "SmarterOS API MCP",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "mcp": "/mcp",
        "openapi": "/openapi.json",
        "governed": MCP_MODE == "governed",
        "rate_limit": {
            "enabled": True,
            "limit_rpm": RATE_LIMIT_RPM,
            "mode": "memory"
        },
        "endpoints": {
            "qwen": "/ai/qwen",
            "openrouter": "/ai/openrouter"
        }
    }

# Endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_enabled": True,
        "mcp_mode": MCP_MODE,
        "rate_limit_enabled": True,
        "rate_limit_rpm": RATE_LIMIT_RPM,
        "qwen_configured": bool(QWEN_API_KEY),
        "openrouter_configured": bool(OPENROUTER_API_KEY)
    }

@app.post("/ai/qwen", response_model=CompletionResponse)
async def qwen_completion(
    request: CompletionRequest,
    auth: str = Depends(verify_token)
):
    """Call Qwen API with governance"""
    if not QWEN_API_KEY:
        raise HTTPException(status_code=503, detail="Qwen API not configured")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "input": {"prompt": request.prompt},
                    "parameters": {"result_format": "text"}
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Qwen API error: {response.text}"
                )
            
            return CompletionResponse(
                success=True,
                governed=MCP_MODE == "governed",
                timestamp=datetime.utcnow().isoformat(),
                result=response.json()
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Qwen API timeout")

@app.post("/ai/openrouter", response_model=CompletionResponse)
async def openrouter_completion(
    request: CompletionRequest,
    auth: str = Depends(verify_token)
):
    """Call OpenRouter API"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=503, detail="OpenRouter API not configured")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://smarteros.cl",
                    "X-Title": "SmarterOS"
                },
                json={
                    "model": request.model,
                    "messages": [{"role": "user", "content": request.prompt}]
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenRouter API error: {response.text}"
                )
            
            return CompletionResponse(
                success=True,
                governed=MCP_MODE == "governed",
                timestamp=datetime.utcnow().isoformat(),
                result=response.json()
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OpenRouter API timeout")

# Include routers
app.include_router(runtime.router)

# Initialize FastAPI-MCP
mcp = FastApiMCP(app)

# Mount MCP server HTTP endpoint
mcp.mount_http()

print("✅ SmarterOS API with MCP initialized")
print(f"✅ MCP Mode: {MCP_MODE}")
print(f"✅ Rate Limiting: ENABLED ({RATE_LIMIT_RPM} RPM)")
print(f"✅ Qwen configured: {bool(QWEN_API_KEY)}")
print(f"✅ OpenRouter configured: {bool(OPENROUTER_API_KEY)}")
print(f"✅ MCP endpoint mounted at: /mcp")
print(f"✅ Runtime Validator endpoint: /mcp/runtime/ingest")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

@app.post("/test/ping")
async def test_ping(auth: str = Depends(verify_token)):
    """Test endpoint for rate limiting"""
    return {"pong": True, "timestamp": datetime.utcnow().isoformat()}
