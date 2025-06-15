# CRUD Operations for Hostel Counselling Backend Database

from .users_crud import create_user, read_users, update_user, delete_user
from .blocks_crud import create_block, read_blocks, update_block, delete_block
from .floors_crud import create_floor, read_floors, update_floor, delete_floor
from .rooms_crud import create_room, read_rooms, update_room, delete_room
from .friends_crud import create_friend, read_friends, update_friend, delete_friend
from .allotments_crud import create_allotment, read_allotments, update_allotment, delete_allotment
from .tenants_crud import create_tenant, read_tenants, update_tenant, delete_tenant
from .connection_pool_async import get_connection_pool_async, init_connection_pool_async, close_connection_pool_async

__all__ = [
    # Users
    'create_user', 'read_users', 'update_user', 'delete_user',
    # Blocks
    'create_block', 'read_blocks', 'update_block', 'delete_block',
    # Floors
    'create_floor', 'read_floors', 'update_floor', 'delete_floor',
    # Rooms
    'create_room', 'read_rooms', 'update_room', 'delete_room',
    # Friends
    'create_friend', 'read_friends', 'update_friend', 'delete_friend',
    # Allotments
    'create_allotment', 'read_allotments', 'update_allotment', 'delete_allotment',
    # Tenants
    'create_tenant', 'read_tenants', 'update_tenant', 'delete_tenant',
    # Connection Pool
    'get_connection_pool_async', 'init_connection_pool_async', 'close_connection_pool_async'
]
