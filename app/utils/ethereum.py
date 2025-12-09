"""Ethereum wallet utilities using web3.py."""

import base64
import hashlib
import os
from typing import Tuple

from cryptography.fernet import Fernet
from eth_account import Account
from web3 import Web3

from app.config import get_settings
from app.exceptions import EncryptionError, InvalidAddressError


def generate_ethereum_wallet() -> Tuple[str, str, str]:
    """
    Generate a new Ethereum wallet.
    
    Returns:
        Tuple containing (address, public_key, private_key)
    """
    Account.enable_unaudited_hdwallet_features()
    account = Account.create()
    
    address = account.address
    private_key = account.key.hex()
    # Convert private key to public key using eth_keys (standardized via eth-account internals check)
    # or simply return the address if public key isn't strictly needed, but requirements said "Store wallet data...".
    # Let's use a safer way if available, or just the address if public key is strictly mapped.
    # Actually, for standard EC usage:
    from eth_keys import keys
    private_key_bytes = account.key
    private_key_obj = keys.PrivateKey(private_key_bytes)
    public_key = private_key_obj.public_key.to_hex()
    
    return address, public_key, private_key


def validate_ethereum_address(address: str) -> bool:
    """
    Validate an Ethereum address.
    
    Args:
        address: Ethereum address to validate
        
    Returns:
        True if valid, raises InvalidAddressError otherwise
    """
    if not Web3.is_address(address):
        raise InvalidAddressError(address, "ethereum")
    
    return True


def get_encryption_key() -> bytes:
    """
    Derive Fernet key from encryption key in settings.
    
    Returns:
        32-byte base64-encoded key for Fernet
    """
    settings = get_settings()
    key = settings.encryption_key.encode()
    
    derived_key = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(derived_key)


def encrypt_private_key(private_key: str) -> str:
    """
    Encrypt a private key for secure storage.
    
    Args:
        private_key: The private key to encrypt
        
    Returns:
        Encrypted private key as base64 string
    """
    try:
        fernet = Fernet(get_encryption_key())
        encrypted = fernet.encrypt(private_key.encode())
        return encrypted.decode()
    except Exception as e:
        raise EncryptionError(f"Failed to encrypt private key: {str(e)}")


def decrypt_private_key(encrypted_key: str) -> str:
    """
    Decrypt a stored private key.
    
    Args:
        encrypted_key: The encrypted private key
        
    Returns:
        Decrypted private key
    """
    try:
        fernet = Fernet(get_encryption_key())
        decrypted = fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        raise EncryptionError(f"Failed to decrypt private key: {str(e)}")
