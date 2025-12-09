"""Wallet MongoDB document model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class NetworkType(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    BSC = "bsc"
    POLYGON = "polygon"


class WalletModel(Document):
    """MongoDB document model for wallets."""
    
    network: NetworkType = Field(..., description="Blockchain network type")
    address: Indexed(str, unique=True) = Field(..., description="Wallet address")
    public_key: str = Field(..., description="Public key")
    encrypted_private_key: str = Field(..., description="Encrypted private key")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "wallets"
        use_state_management = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "network": "ethereum",
                "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f...",
                "public_key": "0x04...",
                "encrypted_private_key": "encrypted_data...",
            }
        }
