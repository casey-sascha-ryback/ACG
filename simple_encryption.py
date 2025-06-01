"""
Simple Encryption Module

This module provides encryption and decryption functionality for the application.
It's designed to be portable and work in any environment.
"""

import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def encrypt_text(text, password, algorithm='aes'):
    """
    Encrypt text using the specified algorithm
    
    Args:
        text (str): Text to encrypt
        password (str): Password for encryption
        algorithm (str): Encryption algorithm to use
        
    Returns:
        tuple: (encrypted_base64, salt_base64)
    """
    # Generate a random salt
    salt = os.urandom(16)
    
    # Derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits for AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    
    # Generate initialization vector
    iv = os.urandom(16)
    
    # Pad text to be a multiple of 16 bytes (AES block size)
    padded_text = text.encode()
    padding_length = 16 - (len(padded_text) % 16)
    padded_text += bytes([padding_length]) * padding_length
    
    # Create AES cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_text) + encryptor.finalize()
    
    # Combine IV and encrypted data
    result = iv + encrypted
    
    # Convert to base64 for storage/transmission
    encrypted_base64 = base64.b64encode(result).decode('utf-8')
    salt_base64 = base64.b64encode(salt).decode('utf-8')
    
    return encrypted_base64, salt_base64

def decrypt_text(encrypted_base64, salt_base64, password, algorithm='aes'):
    """
    Decrypt text using the specified algorithm
    
    Args:
        encrypted_base64 (str): Base64-encoded encrypted data
        salt_base64 (str): Base64-encoded salt
        password (str): Password for decryption
        algorithm (str): Encryption algorithm used
        
    Returns:
        str: Decrypted text
    """
    try:
        # Decode base64
        encrypted_data = base64.b64decode(encrypted_base64)
        salt = base64.b64decode(salt_base64)
        
        # Extract IV (first 16 bytes) and actual encrypted data
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        
        # Derive key from password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        
        # Create AES cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted[-1]
        decrypted = decrypted[:-padding_length]
        
        # Convert bytes to string
        return decrypted.decode('utf-8')
    
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

def available_algorithms():
    """
    Returns a list of available encryption algorithms
    
    Returns:
        list: Available encryption algorithms with info
    """
    return [
        {
            'id': 'aes',
            'name': 'AES-256',
            'description': 'Advanced Encryption Standard with 256-bit key',
            'key_size': 256,
            'mode': 'CBC',
            'strength': 'Very Strong'
        }
    ]