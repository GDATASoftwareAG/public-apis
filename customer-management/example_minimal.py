# Dependency required for OAuth2 token management.
# Install with: pip install authlib
from authlib.integrations.requests_client import OAuth2Session
import time
import os

# ========================================================
# REQUIRED USER CONFIGURATION - MUST BE SET
# ========================================================

# TOKEN_USERNAME: Your authentication username
TOKEN_USERNAME = os.environ.get("TOKEN_USERNAME", "")

# TOKEN_PASSWORD: Your authentication password
TOKEN_PASSWORD = os.environ.get("TOKEN_PASSWORD", "")

# ORGANIZATION_ID: Your organization's unique identifier (UUID format)
ORGANIZATION_ID = os.environ.get("ORGANIZATION_ID", "")

# ========================================================
# REQUEST BODIES - MODIFY AS NEEDED
# ========================================================
LICENSE_REQUEST_BODY = {
    "customer": "New Company Name",
    "email": "john@doe.de",
    "product": "XDR",
}

# ========================================================
# MAIN WORKFLOW EXAMPLE - ADAPT AS NEEDED (SEE readme.md)
# ========================================================
def main():
    # === Step 1: Request an OAuth2 access token with the configured user credentials. ===
    token = fetch_password_token()

    # === Step 2: Initialize an authenticated session (token refresh is handled automatically). ===
    session = create_session(token)

    # === Step 3: Create a new license for the target customer. ===
    response = session.post(build_service_endpoint("/licenses"), json=LICENSE_REQUEST_BODY)
    key = response.json().get("Key")

    # === Step 4: Retrieve setup IDs required during endpoint installation. ===
    response = session.get(build_service_endpoint(f"/licenses/{key}/setup-ids"))
    print(f"Setup IDs: {response.json().get("SetupConfigurations")}")


# ========================================================
# TOKEN HANDLING - NO CHANGES NEEDED
# ========================================================
TOKEN_ENDPOINT = 'https://account.gdata.de/realms/central-public-production/protocol/openid-connect/token'
SERVICE_ENDPOINT = f'https://customer-management.portal.gdata.de/api/v1/organizations/{ORGANIZATION_ID}'


def create_session(token=None):
    session = OAuth2Session(
        client_id = "WebPortal",
        token = token,
        token_endpoint = TOKEN_ENDPOINT,
        update_token = update_token,
    )
    return session


def update_token(token, **kwargs):
    token['expires_at'] = time.time() + token.get('expires_in', 0) - 30


def fetch_password_token():
    session = create_session()
    token = session.fetch_token(
        url=TOKEN_ENDPOINT,
        grant_type="password",
        username=TOKEN_USERNAME,
        password=TOKEN_PASSWORD,
        include_client_id=True,
    )
    update_token(token)
    return token


def build_service_endpoint(path):
    return SERVICE_ENDPOINT + path


if __name__ == "__main__":
    main()
