import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.fernet import Fernet
import os
import logging

def available_algorithms():
    """
    Returns a list of available encryption algorithms
    
    Returns:
        list: Available encryption algorithms with info
    """
    return [
        {
            'id': 'aes',
            'name': 'AES-256-CBC',
            'description': 'Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode',
            'strength': 'Very High',
            'use_case': 'General purpose encryption, industry standard'
        },
        {
            'id': 'fernet',
            'name': 'Fernet (AES-128-CBC)',
            'description': 'Implementation of symmetric authenticated cryptography (AES-128-CBC with HMAC)',
            'strength': 'High',
            'use_case': 'Easy to use, authenticated encryption with high security'
        },
        {
            'id': 'chacha20',
            'name': 'ChaCha20-Poly1305',
            'description': 'Stream cipher with built-in authentication using Poly1305',
            'strength': 'Very High',
            'use_case': 'Efficient encryption on devices without AES hardware acceleration'
        }
    ]

def derive_key(password, salt=None, algorithm='aes'):
    """
    Derive a key from a password using PBKDF2
    
    Args:
        password (str): Password to derive key from
        salt (bytes, optional): Salt for key derivation
        algorithm (str): Encryption algorithm to use
        
    Returns:
        tuple: (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    else:
        if isinstance(salt, str):
            salt = base64.b64decode(salt)
    
    password_bytes = password.encode()
    
    # Determine key length based on algorithm
    if algorithm == 'aes':
        key_length = 32  # 256 bits for AES-256
    elif algorithm == 'fernet':
        key_length = 32  # Fernet uses this for key derivation
    elif algorithm == 'chacha20':
        key_length = 32  # 256 bits for ChaCha20
    else:
        key_length = 32  # Default to 256 bits
    
    # Derive the key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=100000,
    )
    
    key = kdf.derive(password_bytes)
    return key, salt

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
    # Convert text to bytes
    text_bytes = text.encode()
    
    # Derive key and generate salt
    key, salt = derive_key(password, algorithm=algorithm)
    
    if algorithm == 'aes':
        # Generate initialization vector
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad the plaintext (AES requires block size of 16 bytes)
        padder = lambda s: s + (16 - len(s) % 16) * bytes([16 - len(s) % 16])
        padded_data = padder(text_bytes)
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and ciphertext
        result = iv + encrypted_data
        
    elif algorithm == 'fernet':
        # Generate Fernet key from derived key
        fernet_key = base64.urlsafe_b64encode(key)
        f = Fernet(fernet_key)
        
        # Encrypt
        result = f.encrypt(text_bytes)
        
    elif algorithm == 'chacha20':
        # ChaCha20 needs a 16-byte nonce
        nonce = os.urandom(16)
        
        # Use ChaCha20 algorithm
        algorithm = algorithms.ChaCha20(key, nonce)
        encryptor = Cipher(algorithm, mode=None).encryptor()
        
        # Encrypt
        encrypted_data = encryptor.update(text_bytes) + encryptor.finalize()
        
        # Combine nonce and ciphertext
        result = nonce + encrypted_data
        
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Convert to base64 for storage/transmission
    encrypted_base64 = base64.b64encode(result).decode()
    salt_base64 = base64.b64encode(salt).decode()
    
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
    # Convert from base64
    encrypted_data = base64.b64decode(encrypted_base64)
    
    # Derive the key using the provided salt
    key, _ = derive_key(password, salt_base64, algorithm)
    
    if algorithm == 'aes':
        # Extract IV (first 16 bytes) and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = lambda s: s[:-s[-1]]
        plaintext = unpadder(padded_plaintext)
        
    elif algorithm == 'fernet':
        # Generate Fernet key from derived key
        fernet_key = base64.urlsafe_b64encode(key)
        f = Fernet(fernet_key)
        
        # Decrypt
        plaintext = f.decrypt(encrypted_data)
        
    elif algorithm == 'chacha20':
        # Extract nonce (first 16 bytes) and ciphertext
        nonce = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Use ChaCha20 algorithm
        algorithm = algorithms.ChaCha20(key, nonce)
        decryptor = Cipher(algorithm, mode=None).decryptor()
        
        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Convert bytes to string
    return plaintext.decode()

def explain_algorithm(algorithm_id):
    """
    Provide educational information about an encryption algorithm
    
    Args:
        algorithm_id (str): Algorithm ID
        
    Returns:
        dict: Information about the algorithm
    """
    explanations = {
        'aes': {
            'name': 'AES (Advanced Encryption Standard)',
            'full_name': 'AES-256-CBC (Advanced Encryption Standard with 256-bit key in Cipher Block Chaining mode)',
            'history': 'Developed by Belgian cryptographers Joan Daemen and Vincent Rijmen, selected by NIST in 2001.',
            'description': 'A symmetric block cipher that encrypts data in blocks of 128 bits, using key sizes of 128, 192, or 256 bits.',
            'strengths': [
                'Mathematically proven to be highly secure',
                'Widely adopted and scrutinized',
                'Hardware acceleration on modern CPUs',
                'Resistant to known cryptographic attacks'
            ],
            'weaknesses': [
                'Implementation vulnerabilities can exist (side-channel attacks)',
                'Key management is critical',
                'CBC mode can be vulnerable if not implemented correctly'
            ],
            'use_cases': [
                'Government classified information',
                'Financial transactions',
                'Secure communications',
                'Data at rest encryption'
            ],
            'security_level': 'Very High'
        },
        'fernet': {
            'name': 'Fernet',
            'full_name': 'Fernet (AES-128-CBC with HMAC-SHA256)',
            'history': 'Developed as part of the Python cryptography library to provide authenticated encryption.',
            'description': 'A symmetric authenticated encryption system that uses AES-128-CBC for encryption and HMAC-SHA256 for authentication.',
            'strengths': [
                'Combines encryption and authentication',
                'Prevents tampering with ciphertext',
                'Easy to use correctly',
                'Includes timestamp for rotation/expiration'
            ],
            'weaknesses': [
                'Fixed format limits flexibility',
                'Slightly larger output size due to authentication tag',
                'Uses AES-128 (still secure, but less bits than AES-256)'
            ],
            'use_cases': [
                'Session tokens',
                'Password reset tokens',
                'General-purpose data encryption',
                'Applications where ease of use is important'
            ],
            'security_level': 'High'
        },
        'chacha20': {
            'name': 'ChaCha20-Poly1305',
            'full_name': 'ChaCha20-Poly1305 AEAD (Authenticated Encryption with Associated Data)',
            'history': 'ChaCha20 was designed by Daniel J. Bernstein in 2008 as an improvement on his Salsa20 cipher.',
            'description': 'A stream cipher that combines the ChaCha20 algorithm with the Poly1305 authenticator for authenticated encryption.',
            'strengths': [
                'Very fast in software (no hardware acceleration needed)',
                'Designed to resist timing attacks',
                'Strong resistance to cryptanalysis',
                'Authenticated encryption prevents tampering'
            ],
            'weaknesses': [
                'Less hardware support compared to AES',
                'Relatively newer, so less extensively analyzed than AES',
                'Nonce reuse is catastrophic (but true for many algorithms)'
            ],
            'use_cases': [
                'TLS connections (used in TLS 1.3)',
                'Mobile and IoT devices without AES hardware acceleration',
                'High-performance secure communications',
                'VPNs and secure tunneling protocols'
            ],
            'security_level': 'Very High'
        }
    }
    
    return explanations.get(algorithm_id, {
        'name': algorithm_id.upper(),
        'full_name': f'{algorithm_id.upper()} Encryption Algorithm',
        'description': 'Information not available for this algorithm.',
        'security_level': 'Unknown'
    })
