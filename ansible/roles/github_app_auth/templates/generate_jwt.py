#!/usr/bin/env python3
"""
Generate GitHub App JWT token for authentication.
Requires GITHUB_APP_ID and GITHUB_PRIVATE_KEY environment variables.
"""

import os
import sys
import time
import jwt
from cryptography.hazmat.primitives import serialization

def validate_private_key(private_key_str):
    """Validate the private key format."""
    try:
        # Try to load the private key to validate format
        serialization.load_pem_private_key(
            private_key_str.encode(),
            password=None
        )
        return True
    except Exception as e:
        print(f"Error: Invalid private key format: {e}", file=sys.stderr)
        return False

def generate_jwt_token():
    """Generate a JWT token for GitHub App authentication."""
    app_id = os.environ.get('GITHUB_APP_ID')
    private_key = os.environ.get('GITHUB_PRIVATE_KEY')

    if not app_id or not private_key:
        print("Error: GITHUB_APP_ID and GITHUB_PRIVATE_KEY must be set", file=sys.stderr)
        sys.exit(1)

    # Validate private key format
    if not validate_private_key(private_key):
        sys.exit(1)

    # Current time
    now = int(time.time())

    # JWT payload
    payload = {
        'iat': now - 60,  # Issued at time (60 seconds in the past to allow for clock drift)
        'exp': now + 600,  # JWT expiration time (10 minutes maximum)
        'iss': app_id  # GitHub App's identifier
    }

    # Create JWT
    token = jwt.encode(payload, private_key, algorithm='RS256')

    # Print token (will be captured by Ansible)
    print(token)

if __name__ == '__main__':
    generate_jwt_token()
