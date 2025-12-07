import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import httpx

# Tokens desde environment
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MCP_MODE = os.getenv("MCP_MODE", "governed")

app = FastAPI(
    title="SmarterOS API with MCP",
    description="Enterprise API with FastAPI-MCP integration",
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

# Initialize FastAPI-MCP
mcp = FastApiMCP(app)

# Mount MCP server HTTP endpoint
mcp.mount_http()

print("✅ SmarterOS API with MCP initialized")
print(f"✅ MCP Mode: {MCP_MODE}")
print(f"✅ Qwen configured: {bool(QWEN_API_KEY)}")
print(f"✅ OpenRouter configured: {bool(OPENROUTER_API_KEY)}")
print(f"✅ MCP endpoint mounted at: /mcp")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
