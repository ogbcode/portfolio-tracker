"""Wallet service for managing wallet operations."""

from typing import List

from beanie import PydanticObjectId

from app.core.logging import logger
from app.exceptions import InvalidNetworkError, WalletNotFoundError
from app.models.wallet import NetworkType, WalletModel
from app.schemas.wallet import WalletResponse
from app.utils.bitcoin import generate_bitcoin_wallet
from app.utils.bitcoin import encrypt_private_key as encrypt_btc_key
from app.utils.ethereum import encrypt_private_key, generate_ethereum_wallet


class WalletService:
    """Service class for wallet operations."""
    
    async def create_wallet(self, network: NetworkType) -> WalletModel:
        """
        Generate and store a new wallet for the specified network.
        
        Args:
            network: The blockchain network type
            
        Returns:
            The created wallet model
        """
        logger.info(f"Generating new {network.value} wallet")
        
        if network == NetworkType.BITCOIN:
            address, public_key, private_key = generate_bitcoin_wallet()
            encrypted_key = encrypt_btc_key(private_key)
        elif network in (NetworkType.ETHEREUM, NetworkType.BSC, NetworkType.POLYGON):
            address, public_key, private_key = generate_ethereum_wallet()
            encrypted_key = encrypt_private_key(private_key)
        else:
            raise InvalidNetworkError(network)
        
        wallet = WalletModel(
            network=network,
            address=address,
            public_key=public_key,
            encrypted_private_key=encrypted_key,
        )
        
        await wallet.insert()
        logger.info(f"Created wallet {wallet.id} with address {address}")
        
        return wallet
    
    async def get_wallet(self, wallet_id: str) -> WalletModel:
        """
        Retrieve a wallet by its ID.
        
        Args:
            wallet_id: The wallet's MongoDB ID
            
        Returns:
            The wallet model
            
        Raises:
            WalletNotFoundError: If wallet doesn't exist
        """
        try:
            wallet = await WalletModel.get(PydanticObjectId(wallet_id))
        except Exception:
            raise WalletNotFoundError(wallet_id)
        
        if not wallet:
            raise WalletNotFoundError(wallet_id)
        
        return wallet
    
    async def get_all_wallets(self) -> List[WalletModel]:
        """
        Retrieve all wallets.
        
        Returns:
            List of all wallet models
        """
        return await WalletModel.find_all().to_list()
    
    async def delete_wallet(self, wallet_id: str) -> bool:
        """
        Delete a wallet by its ID.
        
        Args:
            wallet_id: The wallet's MongoDB ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            WalletNotFoundError: If wallet doesn't exist
        """
        wallet = await self.get_wallet(wallet_id)
        await wallet.delete()
        logger.info(f"Deleted wallet {wallet_id}")
        return True
    
    def to_response(self, wallet: WalletModel) -> WalletResponse:
        """
        Convert wallet model to response DTO.
        
        Args:
            wallet: The wallet model
            
        Returns:
            Wallet response DTO (excludes private key)
        """
        return WalletResponse(
            id=str(wallet.id),
            network=wallet.network,
            address=wallet.address,
            created_at=wallet.created_at,
        )


wallet_service = WalletService()
