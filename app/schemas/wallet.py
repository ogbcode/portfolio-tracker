"""Wallet request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.wallet import NetworkType


class WalletCreateRequest(BaseModel):
    """Request schema for wallet creation."""
    
    network: NetworkType = Field(..., description="Blockchain network type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "network": "ethereum"
            }
        }


class WalletResponse(BaseModel):
    """Response schema for wallet data (excludes private key)."""
    
    id: str = Field(..., description="Wallet ID")
    network: NetworkType = Field(..., description="Blockchain network type")
    address: str = Field(..., description="Wallet address")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "network": "ethereum",
                "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f...",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class WalletBalanceResponse(BaseModel):
    """Response schema for wallet with balance information."""
    
    id: str = Field(..., description="Wallet ID")
    network: NetworkType = Field(..., description="Blockchain network type")
    address: str = Field(..., description="Wallet address")
    asset: str = Field(default="Native", description="Asset symbol (e.g. ETH, BTC, USDT)")
    balance: str = Field(..., description="Native currency balance")
    balance_usd: float = Field(..., description="Balance value in USD")
    balance_ngn: float = Field(..., description="Balance value in NGN")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "network": "ethereum",
                "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f...",
                "balance": "1.5",
                "balance_usd": 3750.00,
                "balance_ngn": 5625000.00
            }
        }


class PortfolioValueResponse(BaseModel):
    """Response schema for total portfolio value."""
    
    total_value_usd: float = Field(..., description="Total portfolio value in USD")
    total_value_ngn: float = Field(..., description="Total portfolio value in NGN")
    wallets: list[WalletBalanceResponse] = Field(..., description="Individual wallet balances")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_value_usd": 10000.00,
                "total_value_ngn": 15000000.00,
                "wallets": []
            }
        }
