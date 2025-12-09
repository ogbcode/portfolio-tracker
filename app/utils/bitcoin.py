"""Bitcoin wallet utilities using bitcoinlib."""

from typing import Tuple

from bitcoinlib.keys import Key
from bitcoinlib.wallets import Wallet

from app.exceptions import InvalidAddressError
from app.utils.ethereum import encrypt_private_key as encrypt_key


def generate_bitcoin_wallet() -> Tuple[str, str, str]:
    """
    Generate a new Bitcoin wallet.
    
    Returns:
        Tuple containing (address, public_key, private_key)
    """
    key = Key()
    
    address = key.address()
    public_key = key.public_hex
    private_key = key.wif()
    
    return address, public_key, private_key


def validate_bitcoin_address(address: str) -> bool:
    """
    Validate a Bitcoin address.
    
    Args:
        address: Bitcoin address to validate
        
    Returns:
        True if valid, raises InvalidAddressError otherwise
    """
    try:
        key = Key(address)
        if not key.address():
            raise InvalidAddressError(address, "bitcoin")
        return True
    except Exception:
        raise InvalidAddressError(address, "bitcoin")


def encrypt_private_key(private_key: str) -> str:
    """
    Encrypt a Bitcoin private key for secure storage.
    
    Args:
        private_key: The private key (WIF format) to encrypt
        
    Returns:
        Encrypted private key as base64 string
    """
    return encrypt_key(private_key)
