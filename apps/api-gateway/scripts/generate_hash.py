#!/usr/bin/env python3
"""
Generate correct password hash for admin
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_gateway.utils.security import hash_password


def generate_hash():
    """Generate correct hash for admin123"""
    
    password = "admin123"
    correct_hash = hash_password(password)
    
    print(f"Password: {password}")
    print(f"Correct hash: {correct_hash}")
    print(f"Hash length: {len(correct_hash)}")
    
    # The incorrect hash from database  
    incorrect_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LlewY5GyYqVr/VGr1u"
    print(f"\nIncorrect hash from DB: {incorrect_hash}")
    print(f"Incorrect hash length: {len(incorrect_hash)}")
    print(f"\nProblem: The hash should be exactly 60 characters for bcrypt")


if __name__ == "__main__":
    generate_hash()