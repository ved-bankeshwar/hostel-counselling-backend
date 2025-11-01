"""Database configuration and CRUD operations package."""

from . import user
from . import friendship
from . import hostel
from . import block
from . import floor
from . import room
from . import preference
from . import room_assignment

__all__ = [
    'user',
    'friendship',
    'hostel',
    'block',
    'floor',
    'room',
    'preference',
    'room_assignment',
]
