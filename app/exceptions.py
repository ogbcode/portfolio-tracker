"""Custom exception classes for the application."""


class BlockAiException(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class WalletNotFoundError(BlockAiException):
    """Raised when a wallet is not found."""
    
    def __init__(self, wallet_id: str):
        super().__init__(
            message=f"Wallet with ID '{wallet_id}' not found",
            status_code=404,
        )


class InvalidAddressError(BlockAiException):
    """Raised when a blockchain address is invalid."""
    
    def __init__(self, address: str, network: str):
        super().__init__(
            message=f"Invalid {network} address: {address}",
            status_code=400,
        )


class InvalidNetworkError(BlockAiException):
    """Raised when an unsupported network is specified."""
    
    def __init__(self, network: str):
        super().__init__(
            message=f"Unsupported network: {network}. Supported networks: ethereum, bitcoin",
            status_code=400,
        )


class ExternalAPIError(BlockAiException):
    """Raised when an external API call fails."""
    
    def __init__(self, service: str, detail: str):
        super().__init__(
            message=f"External API error from {service}: {detail}",
            status_code=502,
        )


class EncryptionError(BlockAiException):
    """Raised when encryption/decryption fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            message=f"Encryption error: {detail}",
            status_code=500,
        )
