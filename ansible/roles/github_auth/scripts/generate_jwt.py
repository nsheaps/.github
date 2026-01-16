#!/usr/bin/env python3
"""Generate JWT for GitHub App authentication."""

import os
import sys
import time

try:
    import jwt
except ImportError:
    print("Error: PyJWT not installed. Run: pip install PyJWT", file=sys.stderr)
    sys.exit(1)


def generate_jwt() -> str:
    """Generate a JWT for GitHub App authentication."""
    app_id = os.environ.get("GITHUB_APP_ID")
    private_key = os.environ.get("GITHUB_PRIVATE_KEY")

    if not app_id:
        print("Error: GITHUB_APP_ID environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not private_key:
        print("Error: GITHUB_PRIVATE_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # JWT payload
    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued 60 seconds ago (clock skew tolerance)
        "exp": now + (10 * 60),  # Expires in 10 minutes
        "iss": app_id,
    }

    # Generate token
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


if __name__ == "__main__":
    print(generate_jwt())
