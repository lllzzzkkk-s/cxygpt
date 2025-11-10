#!/usr/bin/env python3
"""
Test admin login
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_gateway.utils.security import verify_password


def test_password():
    """Test if the password hash matches"""
    
    # The hash in database
    stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LlewY5GyYqVr/VGr1u"
    
    # Test password
    password = "admin123"
    
    # Verify
    result = verify_password(password, stored_hash)
    print(f"Password verification for 'admin123': {result}")
    
    # Also test with lowercase version (common issue)
    result2 = verify_password("admin123", stored_hash.lower())
    print(f"Password verification with lowercase hash: {result2}")
    
    # Test wrong password
    result3 = verify_password("wrong_password", stored_hash)
    print(f"Password verification for 'wrong_password': {result3}")


if __name__ == "__main__":
    test_password()