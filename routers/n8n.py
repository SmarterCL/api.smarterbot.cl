from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import httpx
import os
import logging

logger = logging.getLogger("smarteros.n8n")

router = APIRouter(prefix="/n8n", tags=["n8n"])

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "https://n8n.smarterbot.cl")
N8N_API_KEY = os.getenv("N8N_API_KEY")


def get_n8n_headers():
    """Get n8n API headers with authentication"""
    if not N8N_API_KEY:
        raise HTTPException(status_code=503, detail="n8n API key not configured")
    
    return {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID or name")
    data: Optional[Dict[str, Any]] = Field(None, description="Input data for workflow")


@router.get("/workflows", summary="List n8n workflows")
async def list_workflows(active: Optional[bool] = None, limit: int = 100):
    """List available n8n workflows"""
    try:
        params = {"limit": limit}
        if active is not None:
            params["active"] = str(active).lower()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{N8N_BASE_URL}/api/v1/workflows",
                headers=get_n8n_headers(),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "ok": True,
                "workflows": data.get("data", []),
                "count": len(data.get("data", []))
            }
    
    except httpx.HTTPError as e:
        logger.error(f"n8n API error: {e}")
        raise HTTPException(status_code=502, detail=f"n8n API error: {str(e)}")


@router.get("/workflows/{workflow_id}", summary="Get workflow details")
async def get_workflow(workflow_id: str):
    """Get details of a specific workflow"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}",
                headers=get_n8n_headers()
            )
            response.raise_for_status()
            
            return {"ok": True, "workflow": response.json()}
    
    except httpx.HTTPError as e:
        logger.error(f"n8n API error: {e}")
        raise HTTPException(status_code=502, detail=f"n8n API error: {str(e)}")


@router.post("/workflows/{workflow_id}/execute", summary="Execute workflow")
async def execute_workflow(workflow_id: str, req: ExecuteWorkflowRequest):
    """
    Execute an n8n workflow with optional input data.
    Returns execution ID for tracking.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/execute",
                headers=get_n8n_headers(),
                json=req.data or {}
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "ok": True,
                "execution_id": result.get("data", {}).get("executionId"),
                "result": result
            }
    
    except httpx.HTTPError as e:
        logger.error(f"n8n execution error: {e}")
        raise HTTPException(status_code=502, detail=f"n8n execution error: {str(e)}")


@router.get("/executions/{execution_id}", summary="Get execution status")
async def get_execution(execution_id: str):
    """Get the status and result of a workflow execution"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{N8N_BASE_URL}/api/v1/executions/{execution_id}",
                headers=get_n8n_headers()
            )
            response.raise_for_status()
            
            return {"ok": True, "execution": response.json()}
    
    except httpx.HTTPError as e:
        logger.error(f"n8n API error: {e}")
        raise HTTPException(status_code=502, detail=f"n8n API error: {str(e)}")


@router.get("/executions", summary="List recent executions")
async def list_executions(limit: int = 20, workflow_id: Optional[str] = None):
    """List recent workflow executions"""
    try:
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{N8N_BASE_URL}/api/v1/executions",
                headers=get_n8n_headers(),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "ok": True,
                "executions": data.get("data", []),
                "count": len(data.get("data", []))
            }
    
    except httpx.HTTPError as e:
        logger.error(f"n8n API error: {e}")
        raise HTTPException(status_code=502, detail=f"n8n API error: {str(e)}")


@router.get("/health", summary="Check n8n API health")
async def n8n_health():
    """Check if n8n API is accessible"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{N8N_BASE_URL}/healthz",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            return {
                "ok": True,
                "status": "healthy",
                "configured": bool(N8N_API_KEY)
            }
    
    except Exception as e:
        logger.error(f"n8n health check failed: {e}")
        return {
            "ok": False,
            "status": "unhealthy",
            "error": str(e),
            "configured": bool(N8N_API_KEY)
        }
