from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import tenants_crud
from .models import (
    CreateTenantRequest,
    ReadTenantsRequest,
    UpdateTenantRequest,
    DeleteTenantRequest
)
from .response_models import (
    CreateTenantResponse,
    ReadTenantsResponse,
    UpdateTenantResponse,
    DeleteTenantResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/create", response_model=CreateTenantResponse)
async def create_tenant_endpoint(request: CreateTenantRequest):
    """Create a new tenant."""
    try:
        result = await tenants_crud.create_tenant(
            user_id=request.user_id,
            room_number=request.room_number,
            block_letter=request.block_letter,
            allotment_id=request.allotment_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadTenantsResponse)
async def read_tenants_endpoint(request: ReadTenantsRequest):
    """Read tenants with optional filters."""
    try:
        result = await tenants_crud.read_tenants(
            user_id=request.user_id,
            room_number=request.room_number,
            block_letter=request.block_letter,
            allotment_id=request.allotment_id,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateTenantResponse)
async def update_tenant_endpoint(request: UpdateTenantRequest):
    """Update a tenant."""
    try:
        result = await tenants_crud.update_tenant(
            user_id=request.user_id,
            room_number=request.room_number,
            block_letter=request.block_letter,
            new_user_id=request.new_user_id,
            new_room_number=request.new_room_number,
            new_block_letter=request.new_block_letter,
            allotment_id=request.allotment_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteTenantResponse)
async def delete_tenant_endpoint(request: DeleteTenantRequest):
    """Delete a tenant."""
    try:
        result = await tenants_crud.delete_tenant(
            user_id=request.user_id,
            room_number=request.room_number,
            block_letter=request.block_letter
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
