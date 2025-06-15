from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import blocks_crud
from .models import (
    CreateBlockRequest,
    ReadBlocksRequest,
    UpdateBlockRequest,
    DeleteBlockRequest
)
from .response_models import (
    CreateBlockResponse,
    ReadBlocksResponse,
    UpdateBlockResponse,
    DeleteBlockResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.post("/create", response_model=CreateBlockResponse)
async def create_block_endpoint(request: CreateBlockRequest):
    """Create a new block."""
    try:
        result = await blocks_crud.create_block(
            block_letter=request.block_letter,
            block_name=request.block_name,
            is_deluxe=request.is_deluxe,
            is_ac=request.is_ac
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadBlocksResponse)
async def read_blocks_endpoint(request: ReadBlocksRequest):
    """Read blocks with optional filters."""
    try:
        result = await blocks_crud.read_blocks(
            block_letter=request.block_letter,
            block_name=request.block_name,
            is_deluxe=request.is_deluxe,
            is_ac=request.is_ac,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateBlockResponse)
async def update_block_endpoint(request: UpdateBlockRequest):
    """Update a block."""
    try:
        result = await blocks_crud.update_block(
            block_letter=request.block_letter,
            block_name=request.block_name,
            is_deluxe=request.is_deluxe,
            is_ac=request.is_ac
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteBlockResponse)
async def delete_block_endpoint(request: DeleteBlockRequest):
    """Delete a block."""
    try:
        result = await blocks_crud.delete_block(block_letter=request.block_letter)
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
