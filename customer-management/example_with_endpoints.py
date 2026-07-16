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
    "interactiveOnboarding": True, # if an interactive onboarding on the website is desired
}

ENDPOINT_REQUEST_BODY = [
    {
        "tenantId": "", # filled on runtime
        "computerName": "WORKSTATION-01",
    },
    {
        "tenantId": "", # filled on runtime
        "computerName": "WORKSTATION-02",
    },
]

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
    print(f"{response.status_code}: {response.content.decode('utf-8')}")

    # === Step 4: Read back the created license to obtain the generated tenant ID. ===
    # Note: Provisioning may take a few seconds, so retry logic can be useful.
    tenant_id = None
    while tenant_id is None:
        time.sleep(5)
        response = session.get(build_service_endpoint(f"/licenses/{key}"))
        tenant_id = response.json().get("TenantId")
    print(f"{response.status_code}: {response.content.decode('utf-8')}")

    # === Step 5: Register an endpoint for this tenant. ===
    # Note: Not required but recommended for endpoint visibility and management.
    body = ENDPOINT_REQUEST_BODY
    for endpoint in body:
        endpoint["tenantId"] = tenant_id
    response = session.post(build_service_endpoint("/endpoints"), json=ENDPOINT_REQUEST_BODY)
    print(f"{response.status_code}: {response.content.decode('utf-8')}")

    # === Step 6: Retrieve setup IDs required during endpoint installation. ===
    response = session.get(build_service_endpoint(f"/licenses/{key}/setup-ids"))
    print(f"Setup IDs: {response.json().get("SetupConfigurations")}")
    print(f"{response.status_code}: {response.content.decode('utf-8')}")

    # === Step 7: List tenant endpoints to verify installation status. ===
    # If installation is complete, fields such as agentId and firstSeen are populated.
    # response = session.get(build_service_endpoint(f"/endpoints?filter=tenantId={tenant_id}"))
    # print(f"{response.status_code}: {response.content.decode('utf-8')}")

    # === Step 8: Complete onboarding for the tenant. ===
    # Note: Only necessary if an interactive onboarding process was started.
    # response = session.delete(build_service_endpoint("/onboardings/{tenant-id}"))
    # print(f"{response.status_code}: {response.content.decode('utf-8')}")


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
