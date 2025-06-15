from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import floors_crud
from .models import (
    CreateFloorRequest,
    ReadFloorsRequest,
    UpdateFloorRequest,
    DeleteFloorRequest
)
from .response_models import (
    CreateFloorResponse,
    ReadFloorsResponse,
    UpdateFloorResponse,
    DeleteFloorResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/floors", tags=["floors"])


@router.post("/create", response_model=CreateFloorResponse)
async def create_floor_endpoint(request: CreateFloorRequest):
    """Create a new floor."""
    try:
        result = await floors_crud.create_floor(
            floor_id=request.floor_id,
            floor_number=request.floor_number,
            block_letter=request.block_letter
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadFloorsResponse)
async def read_floors_endpoint(request: ReadFloorsRequest):
    """Read floors with optional filters."""
    try:
        result = await floors_crud.read_floors(
            floor_id=request.floor_id,
            floor_number=request.floor_number,
            block_letter=request.block_letter,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateFloorResponse)
async def update_floor_endpoint(request: UpdateFloorRequest):
    """Update a floor."""
    try:
        result = await floors_crud.update_floor(
            floor_id=request.floor_id,
            floor_number=request.floor_number,
            block_letter=request.block_letter
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteFloorResponse)
async def delete_floor_endpoint(request: DeleteFloorRequest):
    """Delete a floor."""
    try:
        result = await floors_crud.delete_floor(floor_id=request.floor_id)
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
