from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import rooms_crud
from .models import (
    CreateRoomRequest,
    ReadRoomsRequest,
    UpdateRoomRequest,
    DeleteRoomRequest
)
from .response_models import (
    CreateRoomResponse,
    ReadRoomsResponse,
    UpdateRoomResponse,
    DeleteRoomResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/create", response_model=CreateRoomResponse)
async def create_room_endpoint(request: CreateRoomRequest):
    """Create a new room."""
    try:
        result = await rooms_crud.create_room(
            room_number=request.room_number,
            block_name=request.block_name,
            block_letter=request.block_letter,
            total_beds=request.total_beds,
            floor_id=request.floor_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadRoomsResponse)
async def read_rooms_endpoint(request: ReadRoomsRequest):
    """Read rooms with optional filters."""
    try:
        result = await rooms_crud.read_rooms(
            room_number=request.room_number,
            block_name=request.block_name,
            block_letter=request.block_letter,
            total_beds=request.total_beds,
            floor_id=request.floor_id,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateRoomResponse)
async def update_room_endpoint(request: UpdateRoomRequest):
    """Update a room."""
    try:
        result = await rooms_crud.update_room(
            room_number=request.room_number,
            block_name=request.block_name,
            block_letter=request.block_letter,
            total_beds=request.total_beds,
            floor_id=request.floor_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteRoomResponse)
async def delete_room_endpoint(request: DeleteRoomRequest):
    """Delete a room."""
    try:
        result = await rooms_crud.delete_room(room_number=request.room_number)
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
