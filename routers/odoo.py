from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from odoo_client import odoo_client

router = APIRouter(prefix="/odoo", tags=["odoo"])

class SearchReadRequest(BaseModel):
    model: str = Field(..., description="Odoo model name, e.g. product.product")
    domain: List[Any] = Field(default_factory=list, description="Odoo domain array")
    fields: List[str] = Field(default_factory=list, description="Fields to return")
    limit: int = Field(80, ge=1, le=500, description="Max records")

class CreateRequest(BaseModel):
    model: str
    values: Dict[str, Any]

class WriteRequest(BaseModel):
    model: str
    id: int = Field(..., ge=1)
    values: Dict[str, Any]

class UnlinkRequest(BaseModel):
    model: str
    id: int = Field(..., ge=1)

class GenericCallRequest(BaseModel):
    model: str
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)

@router.post("/search_read")
async def odoo_search_read(payload: SearchReadRequest):
    try:
        return await odoo_client.search_read(payload.model, payload.domain, payload.fields, payload.limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/create")
async def odoo_create(payload: CreateRequest):
    try:
        return await odoo_client.create(payload.model, payload.values)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/write")
async def odoo_write(payload: WriteRequest):
    try:
        return await odoo_client.write(payload.model, payload.id, payload.values)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/unlink")
async def odoo_unlink(payload: UnlinkRequest):
    try:
        return await odoo_client.unlink(payload.model, payload.id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/call")
async def odoo_call(payload: GenericCallRequest):
    try:
        return await odoo_client.call(payload.model, payload.method, payload.params)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
