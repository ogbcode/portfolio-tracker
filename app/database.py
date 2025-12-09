"""MongoDB database connection and initialization."""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings
from app.models.wallet import WalletModel


class Database:
    """MongoDB database manager."""
    
    client: AsyncIOMotorClient = None
    
    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        settings = get_settings()
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        
        await init_beanie(
            database=self.client[settings.mongodb_database],
            document_models=[WalletModel],
        )
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


db = Database()
