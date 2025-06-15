from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import friends_crud
from .models import (
    CreateFriendRequest,
    ReadFriendsRequest,
    UpdateFriendRequest,
    DeleteFriendRequest
)
from .response_models import (
    CreateFriendResponse,
    ReadFriendsResponse,
    UpdateFriendResponse,
    DeleteFriendResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/create", response_model=CreateFriendResponse)
async def create_friend_endpoint(request: CreateFriendRequest):
    """Create a new friend relationship."""
    try:
        result = await friends_crud.create_friend(
            user_id=request.user_id,
            friend_id=request.friend_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadFriendsResponse)
async def read_friends_endpoint(request: ReadFriendsRequest):
    """Read friend relationships with optional filters."""
    try:
        result = await friends_crud.read_friends(
            user_id=request.user_id,
            friend_id=request.friend_id,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateFriendResponse)
async def update_friend_endpoint(request: UpdateFriendRequest):
    """Update a friend relationship."""
    try:
        result = await friends_crud.update_friend(
            user_id=request.user_id,
            friend_id=request.friend_id,
            new_user_id=request.new_user_id,
            new_friend_id=request.new_friend_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteFriendResponse)
async def delete_friend_endpoint(request: DeleteFriendRequest):
    """Delete a friend relationship."""
    try:
        result = await friends_crud.delete_friend(
            user_id=request.user_id,
            friend_id=request.friend_id
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
