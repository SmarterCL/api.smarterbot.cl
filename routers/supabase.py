from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import os
import logging

logger = logging.getLogger("smarteros.supabase")

router = APIRouter(prefix="/supabase", tags=["supabase"])

# Lazy import to avoid dependency issues
def get_supabase():
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)


class QueryRequest(BaseModel):
    table: str = Field(..., description="Table name")
    select: str = Field("*", description="Columns to select (e.g., 'id,name,email')")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters as key-value pairs")
    order: Optional[str] = Field(None, description="Order by column (e.g., 'created_at.desc')")
    limit: Optional[int] = Field(100, description="Limit results", ge=1, le=1000)


class InsertRequest(BaseModel):
    table: str = Field(..., description="Table name")
    data: Dict[str, Any] = Field(..., description="Data to insert")


class UpdateRequest(BaseModel):
    table: str = Field(..., description="Table name")
    filters: Dict[str, Any] = Field(..., description="Filters to match rows")
    data: Dict[str, Any] = Field(..., description="Data to update")


class DeleteRequest(BaseModel):
    table: str = Field(..., description="Table name")
    filters: Dict[str, Any] = Field(..., description="Filters to match rows to delete")


@router.post("/query", summary="Query Supabase table")
async def query_table(req: QueryRequest, supabase=Depends(get_supabase)):
    """Query a Supabase table with filters, ordering, and pagination"""
    try:
        query = supabase.table(req.table).select(req.select)
        
        # Apply filters
        if req.filters:
            for key, value in req.filters.items():
                query = query.eq(key, value)
        
        # Apply ordering
        if req.order:
            if ".desc" in req.order:
                col = req.order.replace(".desc", "")
                query = query.order(col, desc=True)
            else:
                query = query.order(req.order)
        
        # Apply limit
        if req.limit:
            query = query.limit(req.limit)
        
        response = query.execute()
        return {"ok": True, "data": response.data, "count": len(response.data)}
    
    except Exception as e:
        logger.error(f"Supabase query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insert", summary="Insert into Supabase table")
async def insert_row(req: InsertRequest, supabase=Depends(get_supabase)):
    """Insert a new row into a Supabase table"""
    try:
        response = supabase.table(req.table).insert(req.data).execute()
        return {"ok": True, "data": response.data}
    
    except Exception as e:
        logger.error(f"Supabase insert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update", summary="Update Supabase table rows")
async def update_rows(req: UpdateRequest, supabase=Depends(get_supabase)):
    """Update rows in a Supabase table matching filters"""
    try:
        query = supabase.table(req.table).update(req.data)
        
        # Apply filters
        for key, value in req.filters.items():
            query = query.eq(key, value)
        
        response = query.execute()
        return {"ok": True, "data": response.data, "count": len(response.data)}
    
    except Exception as e:
        logger.error(f"Supabase update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete", summary="Delete from Supabase table")
async def delete_rows(req: DeleteRequest, supabase=Depends(get_supabase)):
    """Delete rows from a Supabase table matching filters"""
    try:
        query = supabase.table(req.table).delete()
        
        # Apply filters
        for key, value in req.filters.items():
            query = query.eq(key, value)
        
        response = query.execute()
        return {"ok": True, "deleted": len(response.data)}
    
    except Exception as e:
        logger.error(f"Supabase delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables", summary="List available tables (requires RLS bypass)")
async def list_tables(supabase=Depends(get_supabase)):
    """
    Attempt to list tables from information_schema.
    Note: May require special permissions.
    """
    try:
        # This requires service role key and proper RLS settings
        response = supabase.rpc("get_tables").execute()
        return {"ok": True, "tables": response.data}
    except Exception as e:
        # Fallback: return common tables or error
        logger.warning(f"Cannot list tables: {e}")
        return {
            "ok": False,
            "message": "Table listing requires custom RPC function or direct postgres access",
            "common_tables": ["contacts", "users", "logs"]
        }
