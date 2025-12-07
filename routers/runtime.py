"""
Runtime Validator Ingestion Endpoint
Recibe datos de Open-Scouts y los almacena en Supabase
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
from datetime import datetime

router = APIRouter(prefix="/mcp/runtime", tags=["runtime"])

# Supabase client (lazy initialization)
_supabase_client = None

def get_supabase() -> Client:
    """Lazy initialization de Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise RuntimeError("SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY requeridos")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_client


class LinkValidation(BaseModel):
    url: str
    status_code: int
    redirect_target: Optional[str] = None
    is_external: bool = False
    

class URLDelta(BaseModel):
    url: str
    delta_type: str  # new, removed, modified
    previous_url: Optional[str] = None


class SemanticDelta(BaseModel):
    url: str
    field_name: str
    old_value: Optional[str] = None
    new_value: str
    impact_level: str  # minor, relevant, critical


class RuntimeIngestPayload(BaseModel):
    tenant_id: str
    scout_id: str
    domain: str
    links: List[LinkValidation]
    urls_new: List[str] = []
    urls_removed: List[str] = []
    semantic_changes: List[SemanticDelta] = []
    metadata: Optional[Dict[str, Any]] = None


@router.post("/ingest")
async def ingest_scout_data(payload: RuntimeIngestPayload):
    """
    Endpoint principal para recibir datos de Open-Scouts
    Inserta en las 4 tablas del Runtime Validator
    """
    
    supabase = get_supabase()
    
    try:
        # 1. Crear ejecución
        execution_result = supabase.table("runtime_executions").insert({
            "tenant_id": payload.tenant_id,
            "scout_id": payload.scout_id,
            "domain": payload.domain,
            "status": "completed",
            "metadata": payload.metadata or {}
        }).execute()
        
        execution_id = execution_result.data[0]["id"]
        
        # 2. Insertar validaciones de links
        if payload.links:
            link_records = [
                {
                    "execution_id": execution_id,
                    "url": link.url,
                    "status_code": link.status_code,
                    "redirect_target": link.redirect_target,
                    "is_external": link.is_external
                }
                for link in payload.links
            ]
            supabase.table("runtime_link_validations").insert(link_records).execute()
        
        # 3. Insertar deltas de URLs (nuevas)
        if payload.urls_new:
            url_delta_records = [
                {
                    "execution_id": execution_id,
                    "url": url,
                    "delta_type": "new"
                }
                for url in payload.urls_new
            ]
            supabase.table("runtime_url_deltas").insert(url_delta_records).execute()
        
        # 4. Insertar deltas de URLs (removidas)
        if payload.urls_removed:
            url_removed_records = [
                {
                    "execution_id": execution_id,
                    "url": url,
                    "delta_type": "removed"
                }
                for url in payload.urls_removed
            ]
            supabase.table("runtime_url_deltas").insert(url_removed_records).execute()
        
        # 5. Insertar cambios semánticos
        if payload.semantic_changes:
            semantic_records = [
                {
                    "execution_id": execution_id,
                    "url": change.url,
                    "field_name": change.field_name,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "impact_level": change.impact_level
                }
                for change in payload.semantic_changes
            ]
            supabase.table("runtime_semantic_deltas").insert(semantic_records).execute()
        
        # 6. Crear alertas si hay cambios críticos
        critical_changes = [c for c in payload.semantic_changes if c.impact_level == "critical"]
        broken_links = [l for l in payload.links if l.status_code >= 400]
        
        alerts = []
        
        if broken_links:
            alerts.append({
                "execution_id": execution_id,
                "type": "link_failure",
                "severity": "critical",
                "payload": {
                    "broken_count": len(broken_links),
                    "urls": [l.url for l in broken_links[:5]]
                }
            })
        
        if critical_changes:
            alerts.append({
                "execution_id": execution_id,
                "type": "semantic_critical",
                "severity": "critical",
                "payload": {
                    "changes_count": len(critical_changes),
                    "fields": [c.field_name for c in critical_changes]
                }
            })
        
        if alerts:
            supabase.table("runtime_alerts").insert(alerts).execute()
        
        return {
            "status": "ok",
            "execution_id": execution_id,
            "links_validated": len(payload.links),
            "urls_new": len(payload.urls_new),
            "urls_removed": len(payload.urls_removed),
            "semantic_changes": len(payload.semantic_changes),
            "alerts_created": len(alerts)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def runtime_health():
    """Health check del sistema de runtime"""
    try:
        supabase = get_supabase()
        return {
            "status": "ok",
            "service": "runtime_validator",
            "supabase": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "runtime_validator",
            "supabase": "disconnected",
            "error": str(e)
        }
