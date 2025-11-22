from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client, Client
import httpx
import os
from typing import Optional

app = FastAPI(
    title="Smarter OS API",
    description="Unified contact API for smarterbot.cl and smarterbot.store",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://smarterbot.cl",
        "https://www.smarterbot.cl",
        "https://smarterbot.store",
        "https://www.smarterbot.store",
        "https://app.smarterbot.cl",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM", "no-reply@smarterbot.cl")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "smarterbotcl@gmail.com")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE) if SUPABASE_URL and SUPABASE_SERVICE_ROLE else None


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    message: str = Field(..., min_length=1, max_length=5000, description="Message content")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number (optional)")
    source: Optional[str] = Field(None, max_length=100, description="Source domain")


class ContactResponse(BaseModel):
    ok: bool
    message: str = "Contact submitted successfully"


async def send_resend_emails(data: ContactRequest, domain: str):
    """Send confirmation email to user and notification to admin via Resend"""
    if not RESEND_API_KEY:
        return False
    
    async with httpx.AsyncClient() as client:
        # User confirmation email
        user_email_payload = {
            "from": RESEND_FROM,
            "to": [data.email],
            "subject": "Gracias por contactar a Smarter OS",
            "html": f"""
                <div style="font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;max-width:600px;margin:0 auto">
                    <h2 style="color:#2563eb">¡Gracias, {data.name}!</h2>
                    <p>Recibimos tu mensaje y te responderemos muy pronto.</p>
                    <div style="background:#f3f4f6;padding:1rem;border-radius:8px;margin:1rem 0">
                        <p style="margin:0"><strong>Tu mensaje:</strong></p>
                        <p style="margin:0.5rem 0 0 0;white-space:pre-wrap">{data.message}</p>
                    </div>
                    <p>Puedes acceder al panel central en <a href="https://app.smarterbot.cl" style="color:#2563eb">app.smarterbot.cl</a>.</p>
                    <hr style="border:none;border-top:1px solid #e5e7eb;margin:2rem 0" />
                    <p style="color:#6b7280;font-size:0.875rem">Smarter OS - Automatización inteligente</p>
                </div>
            """,
        }
        
        # Admin notification email
        admin_email_payload = {
            "from": RESEND_FROM,
            "to": [ADMIN_EMAIL],
            "subject": f"Nuevo contacto: {data.name} <{data.email}>",
            "html": f"""
                <div style="font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;max-width:600px;margin:0 auto">
                    <h3 style="color:#2563eb">Nuevo contacto recibido</h3>
                    <table style="width:100%;border-collapse:collapse">
                        <tr><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb"><strong>Nombre:</strong></td><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb">{data.name}</td></tr>
                        <tr><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb"><strong>Email:</strong></td><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb"><a href="mailto:{data.email}">{data.email}</a></td></tr>
                        <tr><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb"><strong>WhatsApp:</strong></td><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb">{data.phone or '-'}</td></tr>
                        <tr><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb"><strong>Source:</strong></td><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb">{data.source or '-'}</td></tr>
                        <tr><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb"><strong>Domain:</strong></td><td style="padding:0.5rem 0;border-bottom:1px solid #e5e7eb">{domain}</td></tr>
                    </table>
                    <div style="background:#f3f4f6;padding:1rem;border-radius:8px;margin:1rem 0">
                        <p style="margin:0"><strong>Mensaje:</strong></p>
                        <p style="margin:0.5rem 0 0 0;white-space:pre-wrap">{data.message}</p>
                    </div>
                </div>
            """,
        }
        
        # Send both emails (fire and forget, don't block on failures)
        try:
            await client.post(
                "https://api.resend.com/emails",
                json=user_email_payload,
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                timeout=5.0,
            )
        except Exception:
            pass
        
        try:
            await client.post(
                "https://api.resend.com/emails",
                json=admin_email_payload,
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                timeout=5.0,
            )
        except Exception:
            pass
    
    return True


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Smarter OS API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": ["/contact", "/health"]
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "supabase": "configured" if supabase else "not configured",
        "resend": "configured" if RESEND_API_KEY else "not configured",
    }


@app.post("/contact", response_model=ContactResponse, status_code=201)
async def create_contact(data: ContactRequest, request: Request):
    """
    Create a new contact submission
    
    - **name**: Full name of the person contacting
    - **email**: Valid email address
    - **message**: Message content (required)
    - **phone**: Optional phone/WhatsApp number
    - **source**: Optional source identifier (e.g., 'smarterbot.cl', 'smarterbot.store')
    """
    
    # Validate Supabase configuration
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    # Get domain from request
    domain = request.headers.get("host", "unknown")
    
    # Insert into Supabase
    try:
        result = supabase.table("contacts").insert({
            "name": data.name,
            "email": data.email,
            "message": data.message,
            "phone": data.phone,
            "source": data.source,
            "domain": domain,
            "status": "new"
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to insert contact")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Send emails asynchronously (non-blocking)
    try:
        await send_resend_emails(data, domain)
    except Exception:
        pass  # Don't fail the request if email sending fails
    
    return ContactResponse(ok=True)


@app.get("/contacts")
async def list_contacts(limit: int = 10, status: Optional[str] = None):
    """
    List recent contacts (requires authentication in production)
    
    - **limit**: Number of contacts to return (default: 10, max: 100)
    - **status**: Filter by status (e.g., 'new', 'contacted', 'closed')
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    query = supabase.table("contacts").select("*").order("created_at", desc=True).limit(min(limit, 100))
    
    if status:
        query = query.eq("status", status)
    
    try:
        result = query.execute()
        return {"contacts": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
