"""Price request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class AssetPriceResponse(BaseModel):
    """Response schema for a single asset price."""
    
    symbol: str = Field(..., description="Asset symbol (e.g., BTC, ETH)")
    price_usd: float = Field(..., description="Price in USD")
    price_ngn: float = Field(..., description="Price in NGN")
    change_24h: Optional[float] = Field(None, description="24-hour price change percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "price_usd": 50000.00,
                "price_ngn": 75000000.00,
                "change_24h": 2.5
            }
        }


class PricesListResponse(BaseModel):
    """Response schema for all asset prices."""
    
    btc: AssetPriceResponse = Field(..., description="Bitcoin price")
    eth: AssetPriceResponse = Field(..., description="Ethereum price")
    bnb: AssetPriceResponse = Field(..., description="BNB price")
    matic: AssetPriceResponse = Field(..., description="MATIC/Polygon price")
    usdt: AssetPriceResponse = Field(..., description="USDT price")
    usdc: AssetPriceResponse = Field(..., description="USDC price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "btc": {"symbol": "BTC", "price_usd": 50000.00, "price_ngn": 75000000.00, "change_24h": 2.5},
                "eth": {"symbol": "ETH", "price_usd": 2500.00, "price_ngn": 3750000.00, "change_24h": 1.8},
                "bnb": {"symbol": "BNB", "price_usd": 300.00, "price_ngn": 450000.00, "change_24h": 1.2},
                "matic": {"symbol": "MATIC", "price_usd": 0.80, "price_ngn": 1200.00, "change_24h": 3.1},
                "usdt": {"symbol": "USDT", "price_usd": 1.00, "price_ngn": 1500.00, "change_24h": 0.01},
                "usdc": {"symbol": "USDC", "price_usd": 1.00, "price_ngn": 1500.00, "change_24h": 0.01}
            }
        }

