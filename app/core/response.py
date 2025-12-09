"""Standardized API response DTOs."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format."""
    
    success: bool = Field(default=True, description="Indicates successful operation")
    message: str = Field(..., description="Human-readable success message")
    data: T = Field(..., description="Response payload")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    success: bool = Field(default=False, description="Indicates failed operation")
    message: str = Field(..., description="Human-readable error message")
    error: str = Field(..., description="Error details")


def success_response(message: str, data: Any) -> dict:
    """Create a standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, error: str) -> dict:
    """Create a standardized error response."""
    return {
        "success": False,
        "message": message,
        "error": error,
    }
