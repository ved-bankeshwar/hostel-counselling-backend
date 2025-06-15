from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import allotments_crud
from .models import (
    CreateAllotmentRequest,
    ReadAllotmentsRequest,
    UpdateAllotmentRequest,
    DeleteAllotmentRequest
)
from .response_models import (
    CreateAllotmentResponse,
    ReadAllotmentsResponse,
    UpdateAllotmentResponse,
    DeleteAllotmentResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/allotments", tags=["allotments"])


@router.post("/create", response_model=CreateAllotmentResponse)
async def create_allotment_endpoint(request: CreateAllotmentRequest):
    """Create a new allotment."""
    try:
        result = await allotments_crud.create_allotment(
            allotment_id=request.allotment_id,
            user_id=request.user_id,
            block_letter=request.block_letter,
            room_number=request.room_number,
            allotment_date=request.allotment_date,
            is_alloted=request.is_alloted
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadAllotmentsResponse)
async def read_allotments_endpoint(request: ReadAllotmentsRequest):
    """Read allotments with optional filters."""
    try:
        result = await allotments_crud.read_allotments(
            allotment_id=request.allotment_id,
            user_id=request.user_id,
            block_letter=request.block_letter,
            room_number=request.room_number,
            allotment_date=request.allotment_date,
            is_alloted=request.is_alloted,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateAllotmentResponse)
async def update_allotment_endpoint(request: UpdateAllotmentRequest):
    """Update an allotment."""
    try:
        result = await allotments_crud.update_allotment(
            allotment_id=request.allotment_id,
            user_id=request.user_id,
            block_letter=request.block_letter,
            room_number=request.room_number,
            allotment_date=request.allotment_date,
            is_alloted=request.is_alloted
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteAllotmentResponse)
async def delete_allotment_endpoint(request: DeleteAllotmentRequest):
    """Delete an allotment."""
    try:
        result = await allotments_crud.delete_allotment(allotment_id=request.allotment_id)
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
