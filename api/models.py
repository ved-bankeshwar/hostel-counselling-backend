from pydantic import BaseModel
from typing import List, Any, Optional


# Response model
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


# User models
class CreateUserRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    registration_number: Optional[str] = None
    name: Optional[str] = None
    group: Optional[int] = None
    course: Optional[str] = None
    year_of_study: Optional[int] = None
    time_to_allotment: Optional[int] = None
    is_alloted: Optional[bool] = None
    mobile_number: Optional[str] = None
    role: Optional[str] = None
    privilages: Optional[List[str]] = None
    rank: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class ReadUsersRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    registration_number: Optional[str] = None
    name: Optional[str] = None
    group: Optional[int] = None
    course: Optional[str] = None
    year_of_study: Optional[int] = None
    time_to_allotment: Optional[int] = None
    is_alloted: Optional[bool] = None
    mobile_number: Optional[str] = None
    role: Optional[str] = None
    privilages: Optional[List[str]] = None
    rank: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateUserRequest(BaseModel):
    user_id: str
    email: Optional[str] = None
    registration_number: Optional[str] = None
    name: Optional[str] = None
    group: Optional[int] = None
    course: Optional[str] = None
    year_of_study: Optional[int] = None
    time_to_allotment: Optional[int] = None
    is_alloted: Optional[bool] = None
    mobile_number: Optional[str] = None
    role: Optional[str] = None
    privilages: Optional[List[str]] = None
    rank: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class DeleteUserRequest(BaseModel):
    user_id: str


# Block models
class CreateBlockRequest(BaseModel):
    block_letter: Optional[str] = None
    block_name: Optional[str] = None
    is_deluxe: Optional[bool] = None
    is_ac: Optional[bool] = None


class ReadBlocksRequest(BaseModel):
    block_letter: Optional[str] = None
    block_name: Optional[str] = None
    is_deluxe: Optional[bool] = None
    is_ac: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateBlockRequest(BaseModel):
    block_letter: str
    block_name: Optional[str] = None
    is_deluxe: Optional[bool] = None
    is_ac: Optional[bool] = None


class DeleteBlockRequest(BaseModel):
    block_letter: str


# Floor models
class CreateFloorRequest(BaseModel):
    floor_id: Optional[int] = None
    floor_number: Optional[int] = None
    block_letter: Optional[str] = None


class ReadFloorsRequest(BaseModel):
    floor_id: Optional[int] = None
    floor_number: Optional[int] = None
    block_letter: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateFloorRequest(BaseModel):
    floor_id: int
    floor_number: Optional[int] = None
    block_letter: Optional[str] = None


class DeleteFloorRequest(BaseModel):
    floor_id: int


# Room models
class CreateRoomRequest(BaseModel):
    room_number: Optional[str] = None
    block_name: Optional[str] = None
    block_letter: Optional[str] = None
    total_beds: Optional[int] = None
    floor_id: Optional[int] = None


class ReadRoomsRequest(BaseModel):
    room_number: Optional[str] = None
    block_name: Optional[str] = None
    block_letter: Optional[str] = None
    total_beds: Optional[int] = None
    floor_id: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateRoomRequest(BaseModel):
    room_number: str
    block_name: Optional[str] = None
    block_letter: Optional[str] = None
    total_beds: Optional[int] = None
    floor_id: Optional[int] = None


class DeleteRoomRequest(BaseModel):
    room_number: str


# Friend models
class CreateFriendRequest(BaseModel):
    user_id: Optional[str] = None
    friend_id: Optional[str] = None


class ReadFriendsRequest(BaseModel):
    user_id: Optional[str] = None
    friend_id: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateFriendRequest(BaseModel):
    user_id: str
    friend_id: str
    new_user_id: Optional[str] = None
    new_friend_id: Optional[str] = None


class DeleteFriendRequest(BaseModel):
    user_id: str
    friend_id: str


# Allotment models
class CreateAllotmentRequest(BaseModel):
    allotment_id: Optional[int] = None
    user_id: Optional[str] = None
    block_letter: Optional[str] = None
    room_number: Optional[str] = None
    allotment_date: Optional[int] = None
    is_alloted: Optional[bool] = None


class ReadAllotmentsRequest(BaseModel):
    allotment_id: Optional[int] = None
    user_id: Optional[str] = None
    block_letter: Optional[str] = None
    room_number: Optional[str] = None
    allotment_date: Optional[int] = None
    is_alloted: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateAllotmentRequest(BaseModel):
    allotment_id: int
    user_id: Optional[str] = None
    block_letter: Optional[str] = None
    room_number: Optional[str] = None
    allotment_date: Optional[int] = None
    is_alloted: Optional[bool] = None


class DeleteAllotmentRequest(BaseModel):
    allotment_id: int


# Tenant models
class CreateTenantRequest(BaseModel):
    user_id: Optional[str] = None
    room_number: Optional[str] = None
    block_letter: Optional[str] = None
    allotment_id: Optional[int] = None


class ReadTenantsRequest(BaseModel):
    user_id: Optional[str] = None
    room_number: Optional[str] = None
    block_letter: Optional[str] = None
    allotment_id: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class UpdateTenantRequest(BaseModel):
    user_id: str
    room_number: str
    block_letter: str
    new_user_id: Optional[str] = None
    new_room_number: Optional[str] = None
    new_block_letter: Optional[str] = None
    allotment_id: Optional[int] = None


class DeleteTenantRequest(BaseModel):
    user_id: str
    room_number: str
    block_letter: str
