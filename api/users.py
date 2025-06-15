from fastapi import APIRouter, HTTPException
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import users_crud
from .models import (
    CreateUserRequest,
    ReadUsersRequest,
    UpdateUserRequest,
    DeleteUserRequest
)
from .response_models import (
    CreateUserResponse,
    ReadUsersResponse,
    UpdateUserResponse,
    DeleteUserResponse
)
from .utils import handle_crud_response

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", response_model=CreateUserResponse)
async def create_user_endpoint(request: CreateUserRequest):
    """Create a new user."""
    try:
        result = await users_crud.create_user(
            user_id=request.user_id,
            email=request.email,
            registration_number=request.registration_number,
            name=request.name,
            group=request.group,
            course=request.course,
            year_of_study=request.year_of_study,
            time_to_allotment=request.time_to_allotment,
            is_alloted=request.is_alloted,
            mobile_number=request.mobile_number,
            role=request.role,
            privilages=request.privilages,
            rank=request.rank,
            created_at=request.created_at,
            updated_at=request.updated_at
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read", response_model=ReadUsersResponse)
async def read_users_endpoint(request: ReadUsersRequest):
    """Read users with optional filters."""
    try:
        result = await users_crud.read_users(
            user_id=request.user_id,
            email=request.email,
            registration_number=request.registration_number,
            name=request.name,
            group=request.group,
            course=request.course,
            year_of_study=request.year_of_study,
            time_to_allotment=request.time_to_allotment,
            is_alloted=request.is_alloted,
            mobile_number=request.mobile_number,
            role=request.role,
            privilages=request.privilages,
            rank=request.rank,
            created_at=request.created_at,
            updated_at=request.updated_at,
            limit=request.limit,
            offset=request.offset
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=UpdateUserResponse)
async def update_user_endpoint(request: UpdateUserRequest):
    """Update a user."""
    try:
        result = await users_crud.update_user(
            user_id=request.user_id,
            email=request.email,
            registration_number=request.registration_number,
            name=request.name,
            group=request.group,
            course=request.course,
            year_of_study=request.year_of_study,
            time_to_allotment=request.time_to_allotment,
            is_alloted=request.is_alloted,
            mobile_number=request.mobile_number,
            role=request.role,
            privilages=request.privilages,
            rank=request.rank,
            created_at=request.created_at,
            updated_at=request.updated_at
        )
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", response_model=DeleteUserResponse)
async def delete_user_endpoint(request: DeleteUserRequest):
    """Delete a user."""
    try:
        result = await users_crud.delete_user(user_id=request.user_id)
        return handle_crud_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
