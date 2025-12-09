"""Application configuration management using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "BlockAi Portfolio Tracker"
    debug: bool = False
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "blockai"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl_seconds: int = 60
    
    # Alchemy API Key
    alchemy_api_key: str = ""
    
    # Encryption
    encryption_key: str = ""
    
    def get_alchemy_rpc_url(self, network: str) -> str:
        """
        Get Alchemy RPC URL for a specific network.
        
        Args:
            network: Network name (ethereum, bsc, polygon, bitcoin)
            
        Returns:
            Alchemy RPC endpoint URL
        """
        network_map = {
            "ethereum": "eth-mainnet",
            "bsc": "bnb-mainnet",
            "polygon": "polygon-mainnet",
            "bitcoin": "btc-mainnet",
        }
        
        alchemy_network = network_map.get(network, "eth-mainnet")
        return f"https://{alchemy_network}.g.alchemy.com/v2/{self.alchemy_api_key}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
