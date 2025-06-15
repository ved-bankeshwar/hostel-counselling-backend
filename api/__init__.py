# API Package for Hostel Counselling Backend

from .users import router as users_router
from .blocks import router as blocks_router
from .floors import router as floors_router
from .rooms import router as rooms_router
from .friends import router as friends_router
from .allotments import router as allotments_router
from .tenants import router as tenants_router

from .models import APIResponse
from .utils import create_response, handle_crud_response

__all__ = [
    # Routers
    'users_router',
    'blocks_router', 
    'floors_router',
    'rooms_router',
    'friends_router',
    'allotments_router',
    'tenants_router',
    # Models and Utils
    'APIResponse',
    'create_response',
    'handle_crud_response'
]
