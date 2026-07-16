# Customer Management API Documentation

## Authorization
```http
Authorization: Bearer <access_token>
```
All endpoints require a Bearer token in the `Authorization` header.

You can obtain the `access_token` from the central token endpoint:

- Token endpoint: `https://account.gdata.de/realms/central-public-production/protocol/openid-connect/token`
- Grant type: `password`
- Client ID: `WebPortal`
- Required credentials: `username` and `password`

An example is provided in the [GitHub Repository](https://github.com/GDATASoftwareAG/public-apis).

## Base URL
```
https://customer-management.portal.gdata.de/api/v1/organizations/{organization-id}/
```


---

## Routes

### Create License

Creates a new license for a customer.

```
POST /licenses
```

**Request Body:**
```json
{
  "customer": "Example Customer",
  "product": "MXDR",
  "email": "contact@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+49123456789",
  "customerReference": "REF-123",
  "interactiveOnboarding": true
}
```

| Field | Type | Required | Description                                                                      |
|-------|------|----------|----------------------------------------------------------------------------------|
| `customer` | string | Yes | Name of the customer this license is issued for                                  |
| `product` | string | Yes | Product type – either `MXDR` or `XDR`                                            |
| `email` | string | Yes | Primary contact email address                                                    |
| `firstName` | string | Yes | First name of the primary contact                                                |
| `lastName` | string | Yes | Last name of the primary contact                                                 |
| `phone` | string | No | Phone number of the primary contact                                              |
| `customerReference` | string | No | An optional reference identifier for the customer                                |
| `interactiveOnboarding` | boolean | No | Indicates whether an interactive onboarding experience on the website is desired |

**Response:** `201 Created`
```json
{
  "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
  "customer": "Example Customer",
  "product": "MXDR",
  "status": "Pending",
  "tenantId": null,
  "createdDate": "2025-06-01T12:00:00Z",
  "onboardingProgressOverall": 0,
  "expiryDate": null,
  "customerReference": "REF-123",
  "partnerName": "Example Partner",
  "nextMilestoneName": "Kick-Off",
  "nextMilestoneDate": "2026-07-13T00:00:00Z",
  "hasOnboardingReport": false
}
```

| Field | Type | Description                                                                                                                                                                                                                                                                                 |
|-------|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `key` | string | The generated license key                                                                                                                                                                                                                                                                   |
| `customer` | string | Name of the customer this license is issued for                                                                                                                                                                                                                                             |
| `product` | string | Product type (`MXDR` or `XDR`)                                                                                                                                                                                                                                                              |
| `status` | string | Current license status: `Pending`, `Onboarding`, `Active`, or `Expired`                                                                                                                                                                                                                     |
| `tenantId` | string (GUID) | The tenant ID, assigned once the tenant has been provisioned. While this is `null`, the license remains in `Pending` status. It can take a few seconds after license creation until a tenant ID is assigned. You can retrieve it via `GET /licenses/{key}`. Required for creating endpoints |
| `createdDate` | string (datetime) | Timestamp of when the license was created                                                                                                                                                                                                                                                   |
| `onboardingProgressOverall` | number | Overall progress of the interactive onboarding (0–100)                                                                                                                                                                                                                                      |
| `expiryDate` | string (datetime) | Date when the license expires, or `null` if no expiry is set                                                                                                                                                                                                                                |
| `customerReference` | string | An optional reference identifier for the customer                                                                                                                                                                                                                                           |
| `partnerName` | string | Name of the partner this customer belongs to                                                                                                                                                                                                                                                |
| `nextMilestoneName` | string | Name of the next milestone in the onboarding process, or `null` if none is set                                                                                                                                                                                                              |
| `nextMilestoneDate` | string (datetime) | Scheduled date of the next onboarding milestone, or `null` if none is set                                                                                                                                                                                                                   |
| `hasOnboardingReport` | boolean | Indicates whether the onboarding report is available on the website. Becomes `true` once onboarding is completed                                                                                                                                                                            |

---

### Get License by Key

Returns details of a specific license.

```
GET /licenses/{key}
```

**Response:** `200 OK` or `404 Not Found`

> The response fields are identical to the response of [Create License](#create-license).

---

### Get All Licenses

Returns a list of all accessible licenses.

```
GET /licenses
```

**Query Parameters:**

| Parameter | Type | Description | Example                      |
|-----------|------|-------------|------------------------------|
| `filter` | string | Gridify filter expression | ``filter=status=onboarding`` |
| `orderBy` | string | Sort order | ``orderBy=customer desc``    |

**Response:** `200 OK`
```json
{
  "count": 1,
  "data": [
    {
      "key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
      "customer": "Example Customer",
      "product": "MXDR",
      "status": "Active",
      "tenantId": "550e8400-e29b-41d4-a716-446655440000",
      "createdDate": "2025-01-15T08:00:00Z",
      "onboardingProgressOverall": 100,
      "expiryDate": null,
      "customerReference": "REF-123"
    }
  ]
}
```

> The fields in each `data[]` entry are identical to the response of [Create License](#create-license).

---

### Get Setup IDs by License Key

Returns setup IDs and names for a specific license.

```
GET /licenses/{key}/setup-ids
```

**Response:** `200 OK`
```json
{
  "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
  "customer": "Example Customer",
  "setupConfigurations": [
    { "setupId": "550e8400-e29b-41d4-a716-446655440000", "name": "Standard Setup" },
    { "setupId": "660e8400-e29b-41d4-a716-446655440001", "name": "Premium Setup" }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `licenseKey` | string | The associated license key |
| `customer` | string | Name of the customer |
| `setupConfigurations` | array | Available setup configurations for this license |
| `setupConfigurations[].setupId` | string (GUID) | Unique identifier of the setup configuration |
| `setupConfigurations[].name` | string | Human-readable name of the setup configuration |

---



### Add Endpoints

Adds a list of endpoints. Each endpoint is initially marked as *not seen*. Already existing endpoints are ignored and will not be affected. Adding an endpoint before the installation is not required, but it allows you to mark endpoints as *critical* and *expected* in advance. This way, you can check whether all the necessary endpoints have been installed.

```
POST /endpoints
```

**Request Body:** (Array)
```json
[
  {
    "tenantId": "550e8400-e29b-41d4-a716-446655440000",
    "computerName": "WORKSTATION-01",
    "fqdn": "workstation-01.example.com",
    "critical": true
  }
]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tenantId` | string (GUID) | Yes | The tenant ID this endpoint belongs to. You can retrieve it via `GET /licenses/{key}` |
| `computerName` | string | No* | Hostname of the computer |
| `fqdn` | string | No* | Fully qualified domain name of the computer |
| `critical` | boolean | No | Indicates whether this is an essential endpoint |

> **Note:** At least one of `computerName` or `fqdn` must be provided.

**Response:** `201 Created`
```json
[
  {
    "id": 1,
    "tenantId": "550e8400-e29b-41d4-a716-446655440000",
    "computerName": "WORKSTATION-01",
    "fqdn": "workstation-01.example.com",
    "critical": true,
    "installationIntended": false,
    "expected": false,
    "agentId": null,
    "firstSeen": null
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique endpoint identifier |
| `tenantId` | string (GUID) | The tenant ID this endpoint belongs to (retrievable via `GET /licenses/{key}`) |
| `computerName` | string | Hostname of the computer |
| `fqdn` | string | Fully qualified domain name of the computer |
| `critical` | boolean | Indicates whether this is an essential endpoint |
| `installationIntended` | boolean | ⚠️ *Currently in development – can be ignored* |
| `expected` | boolean | Whether the endpoint was expected or appeared as an additional one |
| `agentId` | string (GUID) | ID of the installed agent on the device, populated once the agent has been deployed |
| `firstSeen` | string (datetime) | Timestamp of when the agent was first detected on this endpoint |

> **Note:** An existing Agent ID on an endpoint will indicate that the agent has successfully been installed on that device.

---

### Get Endpoint by ID

Returns the endpoint associated with the given ID.

```
GET /endpoints/{id}
```

**Response:** `200 OK` or `404 Not Found`

> The response fields are identical to the response of [Add Endpoints](#add-endpoints).

---

### Get All Endpoints

Returns a paginated list of endpoints.

```
GET /endpoints
```

**Query Parameters:**

| Parameter | Type | Description | Example                                                  |
|-----------|------|-------------|----------------------------------------------------------|
| `filter` | string | Gridify filter expression | ``filter=tenantId=550e8400-e29b-41d4-a716-446655440000`` |
| `orderBy` | string | Sort order | ``orderBy=computerName desc``                               |

**Response:** `200 OK`
```json
{
  "count": 1,
  "data": [
    {
      "id": 1,
      "tenantId": "550e8400-e29b-41d4-a716-446655440000",
      "computerName": "WORKSTATION-01",
      "fqdn": "workstation-01.example.com",
      "critical": true,
      "installationIntended": false,
      "expected": true,
      "agentId": "770e8400-e29b-41d4-a716-446655440002",
      "firstSeen": "2025-03-15T10:30:00Z"
    }
  ]
}
```

> The fields in each `data[]` entry are identical to the response of [Add Endpoints](#add-endpoints).

---

### Update Endpoint

Updates an endpoint. Returns the updated endpoint.

```
PATCH /endpoints/{id}
```

**Request Body:**
```json
{
  "tenantId": "550e8400-e29b-41d4-a716-446655440000",
  "computerName": "WORKSTATION-01-UPDATED",
  "fqdn": "workstation-01-updated.example.com",
  "critical": false
}
```

> The request body fields are identical to those of [Add Endpoints](#add-endpoints).

**Response:** `200 OK`

> The response fields are identical to the response of [Add Endpoints](#add-endpoints).

---

### Delete Endpoint

Deletes an endpoint. Non-existing endpoints are ignored.

```
DELETE /endpoints/{id}
```

**Response:** `204 No Content`

---

### Delete Onboarding

Deletes the onboarding associated with the given tenant ID. Deleting an onboarding will finish it successfully and the associated license will be marked as `Active`. You can retrieve the tenant ID via `GET /licenses/{key}`. The associated endpoints will no longer be accessible via the API. Please use our website to manage endpoints after finishing the onboarding.

[G DATA Web Portal](https://portal.gdata.de/)

```
DELETE /onboardings/{tenant-id}
```

**Response:** `204 No Content`

---

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Resource created |
| `204` | Success without content |
| `400` | Bad request |
| `401` | Not authenticated |
| `403` | Forbidden |
| `404` | Not found |
| `409` | Conflict |
| `500` | Server error |

---

## Other

All other endpoints are not publicly documented and are intended for internal use only. Please use our website for any additional functionality:

[G DATA Web Portal](https://portal.gdata.de/)

---

## Examples

Code examples are maintained in the GitHub repository:

[GitHub Repository](https://github.com/GDATASoftwareAG/public-apis)

---

## Agent Installation

Please refer to the documentation on our website for detailed instructions on how to install the agent on your endpoints:

[Windows installation guide](https://www.gdata.de/help-en/mxdr/QuickGuides/ConfigParamsMSI/) | [Linux installation guide](https://www.gdata.de/help-en/mxdr/QuickGuides/LinuxAgentInstallation/) | [macOS installation guide](https://www.gdata.de/help-en/mxdr/QuickGuides/InstallAgent_Mac/)

The required agent installation files can be downloaded here:

[Windows Clients](https://downloads.gdata.de/R/Setups/mxdr/gdata_agent_setup.msi) | [Linux Clients (DEB)](https://downloads.gdata.de/R/Setups/mxdr/gdata-agent-amd64.deb) | [Linux Clients (RPM)](https://downloads.gdata.de/R/Setups/mxdr/gdata-agent-x86_64.rpm) | [macOS Clients](https://downloads.gdata.de/R/Setups/mxdr/gdata-agent-universal.pkg)

---

## Bug Reports

If you encounter any issues or bugs while using the API, please report them via our website:

[Bug Report](https://bug.gdata.de/)
