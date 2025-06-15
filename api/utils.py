from typing import Any, Optional
from .models import APIResponse


def create_response(
    success: bool = True,
    data: Optional[Any] = None,
    error: Optional[str] = None,
    message: Optional[str] = None,
    status_code: int = 200
) -> APIResponse:
    """Create a standardized API response."""
    if not success and status_code == 200:
        status_code = 400
    
    return APIResponse(
        success=success,
        data=data,
        error=error,
        message=message
    )


def handle_crud_response(result: dict) -> APIResponse:
    """Handle CRUD operation responses and convert to API response."""
    if "error" in result:
        return create_response(
            success=False,
            error=result["error"]
        )
    else:
        return create_response(
            success=True,
            data=result
        )
