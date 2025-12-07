from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime
import os
from supabase import create_client, Client

router = APIRouter(prefix="/mcp/runtime", tags=["Runtime Validator"])

# Supabase client
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(url, key)

# Schemas
class LinkValidation(BaseModel):
    url: HttpUrl
    status_code: int
    redirect_to: Optional[HttpUrl] = None
    is_external: bool
    is_broken: bool

class SemanticChange(BaseModel):
    url: HttpUrl
    change_type: Literal["minor", "relevant", "critical"]
    field: str
    before: str
    after: str
    impact_score: float = Field(ge=0, le=1)

class RuntimeIngestPayload(BaseModel):
    tenant_id: str
    scout_id: str
    domain: str
    execution_started_at: datetime
    execution_completed_at: datetime
    status: Literal["completed", "failed", "partial"]
    links: List[LinkValidation]
    urls_new: List[HttpUrl] = []
    urls_removed: List[HttpUrl] = []
    semantic_changes: List[SemanticChange] = []

class RuntimeIngestResponse(BaseModel):
    status: str
    execution_id: str
    alerts_created: int
    records_inserted: dict

@router.post("/ingest", response_model=RuntimeIngestResponse)
async def ingest_runtime_data(
    payload: RuntimeIngestPayload,
    supabase: Client = Depends(get_supabase)
):
    """
    Ingesta de datos desde Open-Scouts hacia Runtime Validator
    
    Este endpoint recibe datos de crawling y los almacena en:
    - runtime_executions
    - runtime_link_validations
    - runtime_url_deltas
    - runtime_semantic_deltas
    - runtime_alerts (si hay eventos críticos)
    """
    
    try:
        # 1. Verificar que el tenant existe
        tenant_response = supabase.table("tenants") \
            .select("id") \
            .eq("id", payload.tenant_id) \
            .single() \
            .execute()
        
        if not tenant_response.data:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # 2. Insertar ejecución
        execution_response = supabase.table("runtime_executions").insert({
            "tenant_id": payload.tenant_id,
            "scout_id": payload.scout_id,
            "domain": payload.domain,
            "started_at": payload.execution_started_at.isoformat(),
            "completed_at": payload.execution_completed_at.isoformat(),
            "status": payload.status
        }).execute()
        
        execution_id = execution_response.data[0]["id"]
        
        # 3. Insertar validaciones de links
        link_records = []
        for link in payload.links:
            link_records.append({
                "execution_id": execution_id,
                "url": str(link.url),
                "status_code": link.status_code,
                "redirect_to": str(link.redirect_to) if link.redirect_to else None,
                "is_external": link.is_external,
                "is_broken": link.is_broken
            })
        
        if link_records:
            supabase.table("runtime_link_validations").insert(link_records).execute()
        
        # 4. Insertar deltas de URLs
        url_delta_records = []
        for url in payload.urls_new:
            url_delta_records.append({
                "execution_id": execution_id,
                "url": str(url),
                "change_type": "new"
            })
        for url in payload.urls_removed:
            url_delta_records.append({
                "execution_id": execution_id,
                "url": str(url),
                "change_type": "removed"
            })
        
        if url_delta_records:
            supabase.table("runtime_url_deltas").insert(url_delta_records).execute()
        
        # 5. Insertar cambios semánticos
        semantic_records = []
        for change in payload.semantic_changes:
            semantic_records.append({
                "execution_id": execution_id,
                "url": str(change.url),
                "change_type": change.change_type,
                "field": change.field,
                "before_value": change.before,
                "after_value": change.after,
                "impact_score": change.impact_score
            })
        
        if semantic_records:
            supabase.table("runtime_semantic_deltas").insert(semantic_records).execute()
        
        # 6. Crear alertas automáticas para eventos críticos
        alerts = []
        
        # Alertas por links rotos
        broken_links = [l for l in payload.links if l.is_broken]
        if broken_links:
            alerts.append({
                "execution_id": execution_id,
                "type": "link_broken",
                "severity": "critical",
                "message": f"{len(broken_links)} enlaces rotos detectados",
                "payload": {"broken_links": [str(l.url) for l in broken_links]}
            })
        
        # Alertas por cambios semánticos críticos
        critical_changes = [c for c in payload.semantic_changes if c.change_type == "critical"]
        if critical_changes:
            alerts.append({
                "execution_id": execution_id,
                "type": "semantic_change_critical",
                "severity": "critical",
                "message": f"{len(critical_changes)} cambios críticos detectados",
                "payload": {"changes": [
                    {
                        "url": str(c.url),
                        "field": c.field,
                        "before": c.before,
                        "after": c.after
                    } for c in critical_changes
                ]}
            })
        
        alerts_created = 0
        if alerts:
            alert_response = supabase.table("runtime_alerts").insert(alerts).execute()
            alerts_created = len(alert_response.data)
        
        # 7. Respuesta
        return RuntimeIngestResponse(
            status="ingested",
            execution_id=execution_id,
            alerts_created=alerts_created,
            records_inserted={
                "executions": 1,
                "links": len(link_records),
                "url_deltas": len(url_delta_records),
                "semantic_deltas": len(semantic_records),
                "alerts": alerts_created
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ingest failed: {str(e)}"
        )

@router.get("/health")
async def runtime_validator_health():
    """Health check para Runtime Validator"""
    return {
        "service": "Runtime Validator",
        "status": "operational",
        "version": "1.0.0"
    }
