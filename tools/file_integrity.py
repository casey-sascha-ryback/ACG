import hashlib
import logging

def available_algorithms():
    """
    Returns a list of available hashing algorithms for file integrity checking
    
    Returns:
        list: Available hashing algorithms
    """
    return ['md5', 'sha1', 'sha256', 'sha384', 'sha512', 'sha3_256', 'sha3_512']

def calculate_checksum(file, algorithm='sha256'):
    """
    Calculate checksum for a file
    
    Args:
        file: File object (from request.files)
        algorithm (str): Hashing algorithm to use
        
    Returns:
        str: Calculated checksum
    """
    # Reset file pointer to the beginning
    file.seek(0)
    
    # Select the appropriate hashing algorithm
    if algorithm == 'md5':
        hash_obj = hashlib.md5()
    elif algorithm == 'sha1':
        hash_obj = hashlib.sha1()
    elif algorithm == 'sha256':
        hash_obj = hashlib.sha256()
    elif algorithm == 'sha384':
        hash_obj = hashlib.sha384()
    elif algorithm == 'sha512':
        hash_obj = hashlib.sha512()
    elif algorithm == 'sha3_256':
        hash_obj = hashlib.sha3_256()
    elif algorithm == 'sha3_512':
        hash_obj = hashlib.sha3_512()
    else:
        # Default to SHA-256
        hash_obj = hashlib.sha256()
    
    # Read and update hash in chunks for memory efficiency
    for chunk in iter(lambda: file.read(4096), b''):
        hash_obj.update(chunk)
    
    # Reset file pointer to the beginning
    file.seek(0)
    
    # Return the hexadecimal digest
    return hash_obj.hexdigest()

def verify_checksum(file, provided_checksum, algorithm='sha256'):
    """
    Verify if a file's checksum matches the provided value
    
    Args:
        file: File object
        provided_checksum (str): Checksum to verify against
        algorithm (str): Hashing algorithm to use
        
    Returns:
        tuple: (is_valid, calculated_checksum)
    """
    calculated_checksum = calculate_checksum(file, algorithm)
    is_valid = calculated_checksum.lower() == provided_checksum.lower()
    
    return is_valid, calculated_checksum

def explain_algorithm(algorithm):
    """
    Provide educational information about a hashing algorithm
    
    Args:
        algorithm (str): Hashing algorithm name
        
    Returns:
        dict: Information about the algorithm
    """
    explanations = {
        'md5': {
            'name': 'MD5 (Message Digest Algorithm 5)',
            'description': '128-bit hash function developed in 1991. Not cryptographically secure anymore due to vulnerabilities.',
            'use_case': 'Quick file verification where security isn\'t critical',
            'security_level': 'Low - vulnerable to collision attacks'
        },
        'sha1': {
            'name': 'SHA-1 (Secure Hash Algorithm 1)',
            'description': '160-bit hash function developed by the NSA. No longer considered secure for cryptographic applications.',
            'use_case': 'Legacy systems and non-security-critical verifications',
            'security_level': 'Low - vulnerable to collision attacks (demonstrated in 2017)'
        },
        'sha256': {
            'name': 'SHA-256 (Secure Hash Algorithm 256-bit)',
            'description': 'Part of the SHA-2 family, producing a 256-bit hash. Currently considered secure.',
            'use_case': 'Digital signatures, file integrity, and general cryptographic use',
            'security_level': 'High - no known practical attacks'
        },
        'sha384': {
            'name': 'SHA-384 (Secure Hash Algorithm 384-bit)',
            'description': 'Truncated version of SHA-512 producing a 384-bit hash. Very secure.',
            'use_case': 'Applications requiring high security but slightly better performance than SHA-512',
            'security_level': 'Very High - no known practical attacks'
        },
        'sha512': {
            'name': 'SHA-512 (Secure Hash Algorithm 512-bit)',
            'description': 'Part of the SHA-2 family, producing a 512-bit hash. Very secure with longer digest.',
            'use_case': 'High-security applications and sensitive data verification',
            'security_level': 'Very High - no known practical attacks'
        },
        'sha3_256': {
            'name': 'SHA3-256 (Secure Hash Algorithm 3 256-bit)',
            'description': 'Part of the SHA-3 family (formerly Keccak), with a fundamentally different design than SHA-2.',
            'use_case': 'Future-proofing applications, resistance to quantum attacks',
            'security_level': 'Very High - no known practical attacks, different mathematical foundation than SHA-2'
        },
        'sha3_512': {
            'name': 'SHA3-512 (Secure Hash Algorithm 3 512-bit)',
            'description': 'The 512-bit variant of SHA-3, offering maximum security in the SHA-3 family.',
            'use_case': 'Highest security requirements, long-term data integrity',
            'security_level': 'Extremely High - no known practical attacks, different mathematical foundation than SHA-2'
        }
    }
    
    return explanations.get(algorithm, {
        'name': algorithm.upper(),
        'description': 'Information not available for this algorithm.',
        'use_case': 'Varies based on algorithm properties',
        'security_level': 'Unknown'
    })
