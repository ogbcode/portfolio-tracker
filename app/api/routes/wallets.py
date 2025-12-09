"""Wallet API routes."""

from typing import List

from fastapi import APIRouter, status

from app.core.response import SuccessResponse, success_response
from app.schemas.wallet import (
    PortfolioValueResponse,
    WalletBalanceResponse,
    WalletCreateRequest,
    WalletResponse,
)
from app.services.balance_service import balance_service
from app.services.wallet_service import wallet_service


router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post(
    "/generate",
    response_model=SuccessResponse[WalletResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate new wallet",
    description="Generate a new cryptocurrency wallet for the specified network (ethereum or bitcoin).",
)
async def generate_wallet(request: WalletCreateRequest):
    """Generate a new wallet for the specified blockchain network."""
    wallet = await wallet_service.create_wallet(request.network)
    response = wallet_service.to_response(wallet)
    
    return success_response(
        message=f"Successfully created {request.network.value} wallet",
        data=response.model_dump(),
    )


@router.get(
    "",
    response_model=SuccessResponse[List[WalletResponse]],
    summary="List all wallets",
    description="Retrieve a list of all generated wallets.",
)
async def list_wallets():
    """List all wallets."""
    wallets = await wallet_service.get_all_wallets()
    response = [wallet_service.to_response(w) for w in wallets]
    
    return success_response(
        message="Wallets retrieved successfully",
        data=[r.model_dump() for r in response],
    )


@router.get(
    "/balance",
    response_model=SuccessResponse[PortfolioValueResponse],
    summary="Get portfolio value",
    description="Get the total portfolio value across all wallets in USD and NGN.",
)
async def get_portfolio_balance():
    """Get total portfolio value across all wallets."""
    wallets = await wallet_service.get_all_wallets()
    portfolio = await balance_service.get_portfolio_value(wallets)
    
    return success_response(
        message="Portfolio value retrieved successfully",
        data=portfolio.model_dump(),
    )


@router.get(
    "/{wallet_id}",
    response_model=SuccessResponse[WalletResponse],
    summary="Get wallet details",
    description="Retrieve details for a specific wallet by its ID.",
)
async def get_wallet(wallet_id: str):
    """Get wallet details by ID."""
    wallet = await wallet_service.get_wallet(wallet_id)
    response = wallet_service.to_response(wallet)
    
    return success_response(
        message="Wallet retrieved successfully",
        data=response.model_dump(),
    )


@router.get(
    "/{wallet_id}/balance",
    response_model=SuccessResponse[WalletBalanceResponse],
    summary="Get wallet balance",
    description="Get the balance for a specific wallet with USD and NGN conversion. Optionally specify asset (e.g., USDT).",
)
async def get_wallet_balance(wallet_id: str, asset: str = None):
    """Get wallet balance with currency conversion."""
    wallet = await wallet_service.get_wallet(wallet_id)
    balance = await balance_service.get_wallet_balance(wallet, asset)
    
    return success_response(
        message="Wallet balance retrieved successfully",
        data=balance.model_dump(),
    )


@router.delete(
    "/{wallet_id}",
    response_model=SuccessResponse[dict],
    summary="Delete wallet",
    description="Delete a wallet by its ID.",
)
async def delete_wallet(wallet_id: str):
    """Delete a wallet by ID."""
    await wallet_service.delete_wallet(wallet_id)
    
    return success_response(
        message="Wallet deleted successfully",
        data={"deleted": True},
    )
