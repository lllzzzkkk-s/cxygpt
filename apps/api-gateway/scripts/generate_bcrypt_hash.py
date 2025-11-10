#!/usr/bin/env python3
"""
Generate correct password hash using bcrypt directly
"""

import bcrypt

def generate_hash():
    """Generate correct hash for admin123"""
    
    password = "admin123"
    
    # Generate hash
    salt = bcrypt.gensalt()
    correct_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    print(f"Password: {password}")
    print(f"Correct hash: {correct_hash.decode('utf-8')}")
    
    # Verify it works
    if bcrypt.checkpw(password.encode('utf-8'), correct_hash):
        print("✓ Password verification successful")
    
    return correct_hash.decode('utf-8')


if __name__ == "__main__":
    hash_value = generate_hash()