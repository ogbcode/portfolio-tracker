"""Price API routes."""

from fastapi import APIRouter

from app.core.response import SuccessResponse, success_response
from app.schemas.price import PricesListResponse
from app.services.price_service import price_service


router = APIRouter(prefix="/crypto", tags=["Prices"])


@router.get(
    "/prices",
    response_model=SuccessResponse[PricesListResponse],
    summary="Get current prices",
    description="Get current cryptocurrency prices for BTC, ETH, and USDT with NGN conversion.",
)
async def get_prices():
    """Get current cryptocurrency prices with NGN conversion."""
    prices = await price_service.get_all_prices()
    
    return success_response(
        message="Prices retrieved successfully",
        data=prices.model_dump(),
    )
