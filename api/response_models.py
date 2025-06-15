from pydantic import BaseModel
from typing import List, Optional, Any


# Base Response Model
class BaseAPIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


# User Response Models
class UserData(BaseModel):
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


class CreateUserResponse(BaseAPIResponse):
    data: Optional[UserData] = None


class ReadUsersResponse(BaseAPIResponse):
    data: Optional[List[UserData]] = None
    count: Optional[int] = None


class UpdateUserResponse(BaseAPIResponse):
    data: Optional[UserData] = None


class DeleteUserResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[UserData] = None


# Block Response Models
class BlockData(BaseModel):
    block_letter: Optional[str] = None
    block_name: Optional[str] = None
    is_deluxe: Optional[bool] = None
    is_ac: Optional[bool] = None


class CreateBlockResponse(BaseAPIResponse):
    data: Optional[BlockData] = None


class ReadBlocksResponse(BaseAPIResponse):
    data: Optional[List[BlockData]] = None
    count: Optional[int] = None


class UpdateBlockResponse(BaseAPIResponse):
    data: Optional[BlockData] = None


class DeleteBlockResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[BlockData] = None


# Floor Response Models
class FloorData(BaseModel):
    floor_id: Optional[int] = None
    floor_number: Optional[int] = None
    block_letter: Optional[str] = None


class CreateFloorResponse(BaseAPIResponse):
    data: Optional[FloorData] = None


class ReadFloorsResponse(BaseAPIResponse):
    data: Optional[List[FloorData]] = None
    count: Optional[int] = None


class UpdateFloorResponse(BaseAPIResponse):
    data: Optional[FloorData] = None


class DeleteFloorResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[FloorData] = None


# Room Response Models
class RoomData(BaseModel):
    room_number: Optional[str] = None
    block_name: Optional[str] = None
    block_letter: Optional[str] = None
    total_beds: Optional[int] = None
    floor_id: Optional[int] = None


class CreateRoomResponse(BaseAPIResponse):
    data: Optional[RoomData] = None


class ReadRoomsResponse(BaseAPIResponse):
    data: Optional[List[RoomData]] = None
    count: Optional[int] = None


class UpdateRoomResponse(BaseAPIResponse):
    data: Optional[RoomData] = None


class DeleteRoomResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[RoomData] = None


# Friend Response Models
class FriendData(BaseModel):
    user_id: Optional[str] = None
    friend_id: Optional[str] = None


class CreateFriendResponse(BaseAPIResponse):
    data: Optional[FriendData] = None


class ReadFriendsResponse(BaseAPIResponse):
    data: Optional[List[FriendData]] = None
    count: Optional[int] = None


class UpdateFriendResponse(BaseAPIResponse):
    data: Optional[FriendData] = None


class DeleteFriendResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[FriendData] = None


# Allotment Response Models
class AllotmentData(BaseModel):
    allotment_id: Optional[int] = None
    user_id: Optional[str] = None
    block_letter: Optional[str] = None
    room_number: Optional[str] = None
    allotment_date: Optional[int] = None
    is_alloted: Optional[bool] = None


class CreateAllotmentResponse(BaseAPIResponse):
    data: Optional[AllotmentData] = None


class ReadAllotmentsResponse(BaseAPIResponse):
    data: Optional[List[AllotmentData]] = None
    count: Optional[int] = None


class UpdateAllotmentResponse(BaseAPIResponse):
    data: Optional[AllotmentData] = None


class DeleteAllotmentResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[AllotmentData] = None


# Tenant Response Models
class TenantData(BaseModel):
    user_id: Optional[str] = None
    room_number: Optional[str] = None
    block_letter: Optional[str] = None
    allotment_id: Optional[int] = None


class CreateTenantResponse(BaseAPIResponse):
    data: Optional[TenantData] = None


class ReadTenantsResponse(BaseAPIResponse):
    data: Optional[List[TenantData]] = None
    count: Optional[int] = None


class UpdateTenantResponse(BaseAPIResponse):
    data: Optional[TenantData] = None


class DeleteTenantResponse(BaseAPIResponse):
    deleted: Optional[bool] = None
    data: Optional[TenantData] = None


# Health Check Response Models
class HealthCheckData(BaseModel):
    database: Optional[str] = None
    status: Optional[str] = None


class HealthCheckResponse(BaseAPIResponse):
    data: Optional[HealthCheckData] = None


# System Time Response Models
class SystemTimeResponse(BaseAPIResponse):
    data: Optional[Any] = None


# Root Response Models
class RootData(BaseModel):
    version: Optional[str] = None
    status: Optional[str] = None


class RootResponse(BaseAPIResponse):
    data: Optional[RootData] = None
