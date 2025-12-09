"""Balance service for fetching blockchain balances via public RPCs."""

from typing import Dict, List, Optional
from decimal import Decimal

import httpx

from app.cache import cache
from app.core.logging import logger
from app.exceptions import ExternalAPIError, BlockAiException
from app.models.wallet import NetworkType, WalletModel
from app.schemas.wallet import PortfolioValueResponse, WalletBalanceResponse
from app.services.price_service import price_service


# Public RPC Endpoints
PUBLIC_RPC_URLS = {
    "ethereum": "https://eth.llamarpc.com",
    "bsc": "https://bsc-dataseed.binance.org",
    "polygon": "https://polygon-rpc.com",
    "bitcoin": "https://blockstream.info/api",
}

# Native assets for each network
NATIVE_ASSETS = {
    "ethereum": "ETH",
    "bsc": "BNB",
    "polygon": "MATIC",
    "bitcoin": "BTC",
}

# Token Configuration
TOKEN_CONFIG = {
    "ethereum": {
        "usdt": {
            "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", 
            "decimals": 6
        },
        "usdc": {
            "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "decimals": 6
        }
    },
    "bsc": {
        "usdt": {
            "address": "0x55d398326f99059fF775485246999027B3197955", 
            "decimals": 18
        },
        "usdc": {
             "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
             "decimals": 18
        }
    },
    "polygon": {
        "usdt": {
            "address": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 
            "decimals": 6
        },
        "usdc": {
            "address": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
            "decimals": 6
        }
    }
}

BALANCE_OF_SELECTOR = "0x70a08231"


class BalanceService:
    """Service class for blockchain balance operations via public RPCs."""
    
    def _get_rpc_url(self, network: str) -> str:
        """Get public RPC URL for a network."""
        url = PUBLIC_RPC_URLS.get(network)
        if not url:
            raise BlockAiException(f"No RPC URL configured for network: {network}", 400)
        return url
    
    def _get_network_str(self, network: NetworkType) -> str:
        """Convert NetworkType enum to string for lookups."""
        if network == NetworkType.ETHEREUM:
            return "ethereum"
        elif network == NetworkType.BSC:
            return "bsc"
        elif network == NetworkType.POLYGON:
            return "polygon"
        elif network == NetworkType.BITCOIN:
            return "bitcoin"
        return "unknown"
    
    def _is_native_asset(self, asset: str) -> bool:
        """Check if an asset is a native currency of any chain."""
        return asset.upper() in NATIVE_ASSETS.values()
    
    def _get_native_asset_network(self, asset: str) -> Optional[str]:
        """Get the network name for a native asset."""
        asset_upper = asset.upper()
        for network, native in NATIVE_ASSETS.items():
            if native == asset_upper:
                return network
        return None

    async def _get_token_balance(self, address: str, network: str, token_symbol: str) -> Decimal:
        """
        Fetch ERC20/BEP20 token balance using eth_call.
        
        Args:
            address: Wallet address
            network: Network name
            token_symbol: Token symbol (e.g. 'usdt')
            
        Returns:
            Balance in token units
        """
        token_info = TOKEN_CONFIG.get(network, {}).get(token_symbol.lower())
        if not token_info:
            raise BlockAiException(
                message=f"Token {token_symbol} is not configured for {network}",
                status_code=400
            )
            
        contract_address = token_info["address"]
        decimals = token_info["decimals"]
        
        rpc_url = self._get_rpc_url(network)
        
        cache_key = f"balance:{network}:{token_symbol}:{address}"
        cached = await cache.get(cache_key)
        if cached is not None:
             return Decimal(str(cached))

        data_payload = f"{BALANCE_OF_SELECTOR}{address[2:].zfill(64)}"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "eth_call",
                        "params": [
                            {
                                "to": contract_address,
                                "data": data_payload
                            },
                            "latest"
                        ]
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    error_msg = data["error"].get("message", str(data["error"]))
                    logger.warning(f"RPC token error on {network}: {error_msg}")
                    raise ExternalAPIError("RPC", error_msg)
                
                result_hex = data.get("result", "0x0")
                if result_hex == "0x" or result_hex is None:
                    result_hex = "0x0"
                    
                balance_raw = int(result_hex, 16)
                balance = Decimal(balance_raw) / Decimal(10 ** decimals)
                
                await cache.set(cache_key, float(balance), ttl=30)
                
                return balance
                
        except httpx.HTTPError as e:
            error_msg = f"HTTP error fetching {token_symbol} on {network}: {str(e)}"
            logger.error(error_msg)
            raise ExternalAPIError("RPC", error_msg)

    async def _get_evm_balance(self, address: str, network: str) -> Decimal:
        """
        Fetch native balance using public RPC eth_getBalance method.
        
        Args:
            address: Wallet address
            network: Network name
            
        Returns:
            Balance in native currency
        """
        rpc_url = self._get_rpc_url(network)
        
        cache_key = f"balance:{network}:{address}"
        cached = await cache.get(cache_key)
        if cached:
            return Decimal(str(cached))
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "eth_getBalance",
                        "params": [address, "latest"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    error_msg = data["error"].get("message", str(data["error"]))
                    raise ExternalAPIError("RPC", error_msg)
                
                result = data.get("result")
                if not result:
                    raise ExternalAPIError("RPC", "No result in RPC response")
                
                balance_wei = int(result, 16)
                balance = Decimal(balance_wei) / Decimal(10 ** 18)
                
                await cache.set(cache_key, float(balance), ttl=30)
                
                return balance
        except httpx.HTTPError as e:
            error_msg = f"HTTP error fetching {network} balance: {str(e)}"
            logger.error(error_msg)
            raise ExternalAPIError("RPC", error_msg)
    
    async def _get_btc_balance(self, address: str) -> Decimal:
        """
        Fetch Bitcoin balance using Blockstream API.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Balance in BTC
        """
        cache_key = f"balance:bitcoin:{address}"
        cached = await cache.get(cache_key)
        if cached:
            return Decimal(str(cached))
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{PUBLIC_RPC_URLS['bitcoin']}/address/{address}"
                )
                response.raise_for_status()
                data = response.json()
                
                chain = data.get("chain_stats", {})
                mempool = data.get("mempool_stats", {})
                
                funded = chain.get("funded_txo_sum", 0) + mempool.get("funded_txo_sum", 0)
                spent = chain.get("spent_txo_sum", 0) + mempool.get("spent_txo_sum", 0)
                balance_satoshi = funded - spent
                
                balance = Decimal(balance_satoshi) / Decimal(100_000_000)
                
                await cache.set(cache_key, float(balance), ttl=30)
                
                return balance
        except httpx.HTTPError as e:
            error_msg = f"HTTP error fetching BTC balance: {str(e)}"
            logger.error(error_msg)
            raise ExternalAPIError("Blockstream", error_msg)
    
    async def get_wallet_balance(self, wallet: WalletModel, asset: Optional[str] = None) -> WalletBalanceResponse:
        """
        Get balance for a wallet with USD and NGN conversion.
        
        Args:
            wallet: Wallet model
            asset: Optional asset symbol (e.g. USDT) to fetch instead of native
            
        Returns:
            Wallet balance response with currency conversions
        """
        network = wallet.network
        network_str = self._get_network_str(network)
        
        target_asset = asset.upper() if asset else None
        
        if not target_asset:
            target_asset = NATIVE_ASSETS.get(network_str, "UNKNOWN")
        
        if self._is_native_asset(target_asset):
            expected_network = self._get_native_asset_network(target_asset)
            if expected_network and expected_network != network_str:
                raise BlockAiException(
                    message=f"Asset {target_asset} is the native currency of {expected_network}, not {network_str}",
                    status_code=400
                )
            
            if network == NetworkType.BITCOIN:
                balance = await self._get_btc_balance(wallet.address)
                symbol = "BTC"
            elif network == NetworkType.ETHEREUM:
                balance = await self._get_evm_balance(wallet.address, "ethereum")
                symbol = "ETH"
            elif network == NetworkType.BSC:
                balance = await self._get_evm_balance(wallet.address, "bsc")
                symbol = "BNB"
            elif network == NetworkType.POLYGON:
                balance = await self._get_evm_balance(wallet.address, "polygon")
                symbol = "MATIC"
            else:
                balance = Decimal(0)
                symbol = "UNKNOWN"
        else:
            if network == NetworkType.BITCOIN:
                raise BlockAiException(
                    message=f"Asset {target_asset} is not supported on Bitcoin network",
                    status_code=400
                )
            
            if target_asset.lower() not in TOKEN_CONFIG.get(network_str, {}):
                raise BlockAiException(
                    message=f"Asset {target_asset} is not supported on {network.value}",
                    status_code=400
                )

            balance = await self._get_token_balance(wallet.address, network_str, target_asset)
            symbol = target_asset
        
        price_usd = await price_service.get_price_for_symbol(symbol)
        ngn_rate = await price_service.get_ngn_rate()
        
        balance_usd = float(balance) * price_usd
        balance_ngn = balance_usd * ngn_rate
        
        return WalletBalanceResponse(
            id=str(wallet.id),
            network=wallet.network,
            address=wallet.address,
            asset=symbol,
            balance=str(balance),
            balance_usd=round(balance_usd, 2),
            balance_ngn=round(balance_ngn, 2),
        )
    
    async def get_portfolio_value(self, wallets: List[WalletModel]) -> PortfolioValueResponse:
        """Calculate total portfolio value across all wallets."""
        import asyncio
        
        async def fetch_wallet_balances(wallet: WalletModel) -> List[WalletBalanceResponse]:
            results = []
            network_str = self._get_network_str(wallet.network)
            
            # Build list of tasks for this wallet
            tasks = [self.get_wallet_balance(wallet)]  # Native
            
            if wallet.network != NetworkType.BITCOIN:
                tasks.append(self.get_wallet_balance(wallet, asset="USDT"))
                tasks.append(self.get_wallet_balance(wallet, asset="USDC"))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for resp in responses:
                if isinstance(resp, Exception):
                    logger.error(f"Balance fetch error for wallet {wallet.id}: {resp}")
                    continue
                if float(resp.balance) > 0 or resp.asset in ["ETH", "BTC", "BNB", "MATIC"]:
                    results.append(resp)
            
            return results
        
        # Fetch all wallets in parallel
        all_results = await asyncio.gather(
            *[fetch_wallet_balances(w) for w in wallets],
            return_exceptions=True
        )
        
        wallet_balances = []
        total_usd = 0.0
        total_ngn = 0.0
        
        for result in all_results:
            if isinstance(result, Exception):
                logger.error(f"Portfolio fetch error: {result}")
                continue
            for balance in result:
                wallet_balances.append(balance)
                total_usd += balance.balance_usd
                total_ngn += balance.balance_ngn
        
        return PortfolioValueResponse(
            total_value_usd=round(total_usd, 2),
            total_value_ngn=round(total_ngn, 2),
            wallets=wallet_balances,
        )


balance_service = BalanceService()
