"""Price service for fetching cryptocurrency prices."""

from typing import Dict, Any, List

import httpx

from app.cache import cache
from app.core.logging import logger
from app.exceptions import ExternalAPIError
from app.schemas.price import AssetPriceResponse, PricesListResponse


BINANCE_API_URL = "https://api.binance.com/api/v3"
QUIDAX_API_URL = "https://app.quidax.io/api/v1"

CACHE_KEY_PRICES = "crypto:prices"
CACHE_KEY_NGN_RATE = "crypto:ngn_rate"

REQUIRED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "MATICUSDT", "USDCUSDT"]


class PriceService:
    
    async def get_all_binance_tickers(self) -> Dict[str, Dict[str, Any]]:
        """Fetch all tickers from Binance and filter the ones we need."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{BINANCE_API_URL}/ticker/24hr")
                response.raise_for_status()
                data = response.json()
                
                result = {}
                for ticker in data:
                    symbol = ticker["symbol"]
                    if symbol in REQUIRED_SYMBOLS:
                        result[symbol] = {
                            "price": float(ticker["lastPrice"]),
                            "change_24h": float(ticker["priceChangePercent"]),
                        }
                
                return result
        except httpx.HTTPError as e:
            logger.error(f"Binance API error: {e}")
            raise ExternalAPIError("Binance", str(e))
    
    async def get_quidax_ticker(self, market: str) -> Dict[str, Any]:
        """Fetch ticker data from Quidax."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{QUIDAX_API_URL}/markets/tickers/{market}")
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "error":
                    raise ExternalAPIError("Quidax", data.get("message", "Unknown error"))
                
                ticker = data["data"]["ticker"]
                return {
                    "buy": float(ticker["buy"]),
                    "sell": float(ticker["sell"]),
                    "last": float(ticker["last"]),
                }
        except httpx.HTTPError as e:
            logger.error(f"Quidax API error for {market}: {e}")
            raise ExternalAPIError("Quidax", str(e))
        except (KeyError, ValueError) as e:
            logger.error(f"Quidax response parsing error: {e}")
            raise ExternalAPIError("Quidax", f"Invalid response: {e}")
    
    async def get_ngn_rate(self) -> float:
        """Fetch USD to NGN exchange rate."""
        cached_rate = await cache.get(CACHE_KEY_NGN_RATE)
        if cached_rate:
            return cached_rate
        
        try:
            ticker = await self.get_quidax_ticker("usdtngn")
            rate = ticker["last"]
            await cache.set(CACHE_KEY_NGN_RATE, rate, ttl=300)
            return rate
        except ExternalAPIError:
            logger.warning("Quidax unavailable, using fallback NGN rate")
            return 1500.0
    
    async def get_all_prices(self) -> PricesListResponse:
        """Fetch all crypto prices with NGN conversion."""
        cached = await cache.get(CACHE_KEY_PRICES)
        if cached:
            return PricesListResponse(**cached)
        
        logger.info("Fetching prices from Binance...")
        
        try:
            tickers = await self.get_all_binance_tickers()
        except ExternalAPIError as e:
            logger.error(f"Failed to fetch Binance tickers: {e}")
            tickers = {}
        
        prices = {
            "btc": tickers.get("BTCUSDT", {"price": 0.0, "change_24h": 0.0}),
            "eth": tickers.get("ETHUSDT", {"price": 0.0, "change_24h": 0.0}),
            "bnb": tickers.get("BNBUSDT", {"price": 0.0, "change_24h": 0.0}),
            "matic": tickers.get("MATICUSDT", {"price": 0.0, "change_24h": 0.0}),
            "usdc": tickers.get("USDCUSDT", {"price": 0.0, "change_24h": 0.0}),
            "usdt": {"price": 1.0, "change_24h": 0.0},
        }
        
        ngn_rate = await self.get_ngn_rate()
        
        def make_response(symbol: str, data: Dict[str, Any]) -> AssetPriceResponse:
            return AssetPriceResponse(
                symbol=symbol,
                price_usd=data["price"],
                price_ngn=data["price"] * ngn_rate,
                change_24h=data["change_24h"],
            )
        
        result = {
            "btc": make_response("BTC", prices["btc"]),
            "eth": make_response("ETH", prices["eth"]),
            "bnb": make_response("BNB", prices["bnb"]),
            "matic": make_response("MATIC", prices["matic"]),
            "usdc": make_response("USDC", prices["usdc"]),
            "usdt": make_response("USDT", prices["usdt"]),
        }
        
        cache_data = {k: v.model_dump() for k, v in result.items()}
        await cache.set(CACHE_KEY_PRICES, cache_data, ttl=30)
        
        return PricesListResponse(**result)
    
    async def get_price_for_symbol(self, symbol: str) -> float:
        """Get USD price for a specific symbol."""
        prices = await self.get_all_prices()
        symbol_lower = symbol.lower()
        
        if hasattr(prices, symbol_lower):
            price_obj = getattr(prices, symbol_lower)
            return price_obj.price_usd
        
        return 0.0


price_service = PriceService()
