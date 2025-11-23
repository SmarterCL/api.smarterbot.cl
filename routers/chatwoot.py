from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
import httpx
import os
import logging

logger = logging.getLogger("smarteros.chatwoot")

router = APIRouter(prefix="/chatwoot", tags=["chatwoot"])

CHATWOOT_BASE_URL = os.getenv("CHATWOOT_BASE_URL", "https://chatwoot.smarterbot.cl")
CHATWOOT_TOKEN = os.getenv("CHATWOOT_TOKEN")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
CHATWOOT_INBOX_ID = os.getenv("CHATWOOT_INBOX_ID")


def get_chatwoot_headers():
    """Get Chatwoot API headers with authentication"""
    if not CHATWOOT_TOKEN:
        raise HTTPException(status_code=503, detail="Chatwoot token not configured")
    
    return {
        "api_access_token": CHATWOOT_TOKEN,
        "Content-Type": "application/json"
    }


class CreateContactRequest(BaseModel):
    name: str = Field(..., description="Contact name")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone_number: Optional[str] = Field(None, description="Phone number (with country code)")
    custom_attributes: Optional[Dict[str, Any]] = Field(None, description="Custom attributes")


class CreateConversationRequest(BaseModel):
    contact_id: Optional[int] = Field(None, description="Existing contact ID")
    inbox_id: Optional[int] = Field(None, description="Inbox ID (defaults to env)")
    message: str = Field(..., description="First message content")
    source_id: Optional[str] = Field(None, description="External source identifier")


class SendMessageRequest(BaseModel):
    conversation_id: int = Field(..., description="Conversation ID")
    content: str = Field(..., description="Message content")
    message_type: str = Field("outgoing", description="Message type: incoming or outgoing")
    private: bool = Field(False, description="Private note (only visible to agents)")


@router.post("/contacts", summary="Create Chatwoot contact")
async def create_contact(req: CreateContactRequest):
    """Create a new contact in Chatwoot"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    try:
        payload = {"name": req.name}
        if req.email:
            payload["email"] = req.email
        if req.phone_number:
            payload["phone_number"] = req.phone_number
        if req.custom_attributes:
            payload["custom_attributes"] = req.custom_attributes
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts",
                headers=get_chatwoot_headers(),
                json=payload
            )
            response.raise_for_status()
            
            return {"ok": True, "contact": response.json().get("payload")}
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot contact creation error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.get("/contacts", summary="List Chatwoot contacts")
async def list_contacts(page: int = 1, sort: str = "name"):
    """List contacts from Chatwoot"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts",
                headers=get_chatwoot_headers(),
                params={"page": page, "sort": sort}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "ok": True,
                "contacts": data.get("payload", []),
                "meta": data.get("meta", {})
            }
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot API error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.get("/contacts/{contact_id}", summary="Get contact details")
async def get_contact(contact_id: int):
    """Get details of a specific contact"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts/{contact_id}",
                headers=get_chatwoot_headers()
            )
            response.raise_for_status()
            
            return {"ok": True, "contact": response.json().get("payload")}
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot API error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.post("/conversations", summary="Create Chatwoot conversation")
async def create_conversation(req: CreateConversationRequest):
    """Create a new conversation in Chatwoot"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    inbox_id = req.inbox_id or CHATWOOT_INBOX_ID
    if not inbox_id:
        raise HTTPException(status_code=400, detail="Inbox ID required")
    
    try:
        payload = {
            "inbox_id": int(inbox_id),
            "message": req.message
        }
        if req.contact_id:
            payload["contact_id"] = req.contact_id
        if req.source_id:
            payload["source_id"] = req.source_id
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations",
                headers=get_chatwoot_headers(),
                json=payload
            )
            response.raise_for_status()
            
            return {"ok": True, "conversation": response.json()}
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot conversation creation error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.get("/conversations", summary="List conversations")
async def list_conversations(status: str = "open", page: int = 1):
    """List conversations from Chatwoot"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations",
                headers=get_chatwoot_headers(),
                params={"status": status, "page": page}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "ok": True,
                "conversations": data.get("data", {}).get("payload", []),
                "meta": data.get("data", {}).get("meta", {})
            }
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot API error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.post("/conversations/{conversation_id}/messages", summary="Send message to conversation")
async def send_message(conversation_id: int, req: SendMessageRequest):
    """Send a message to a Chatwoot conversation"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    try:
        payload = {
            "content": req.content,
            "message_type": req.message_type,
            "private": req.private
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages",
                headers=get_chatwoot_headers(),
                json=payload
            )
            response.raise_for_status()
            
            return {"ok": True, "message": response.json()}
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot message send error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.get("/conversations/{conversation_id}/messages", summary="Get conversation messages")
async def get_messages(conversation_id: int):
    """Get messages from a Chatwoot conversation"""
    if not CHATWOOT_ACCOUNT_ID:
        raise HTTPException(status_code=503, detail="Chatwoot account ID not configured")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages",
                headers=get_chatwoot_headers()
            )
            response.raise_for_status()
            
            return {"ok": True, "messages": response.json().get("payload", [])}
    
    except httpx.HTTPError as e:
        logger.error(f"Chatwoot API error: {e}")
        raise HTTPException(status_code=502, detail=f"Chatwoot API error: {str(e)}")


@router.get("/health", summary="Check Chatwoot API health")
async def chatwoot_health():
    """Check if Chatwoot API is accessible and configured"""
    try:
        configured = all([CHATWOOT_TOKEN, CHATWOOT_ACCOUNT_ID, CHATWOOT_INBOX_ID])
        
        if not configured:
            return {
                "ok": False,
                "status": "not_configured",
                "missing": [
                    k for k, v in {
                        "CHATWOOT_TOKEN": CHATWOOT_TOKEN,
                        "CHATWOOT_ACCOUNT_ID": CHATWOOT_ACCOUNT_ID,
                        "CHATWOOT_INBOX_ID": CHATWOOT_INBOX_ID
                    }.items() if not v
                ]
            }
        
        # Test API connectivity
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts",
                headers=get_chatwoot_headers(),
                params={"page": 1}
            )
            response.raise_for_status()
            
            return {"ok": True, "status": "healthy", "configured": True}
    
    except Exception as e:
        logger.error(f"Chatwoot health check failed: {e}")
        return {
            "ok": False,
            "status": "unhealthy",
            "error": str(e),
            "configured": bool(CHATWOOT_TOKEN)
        }
