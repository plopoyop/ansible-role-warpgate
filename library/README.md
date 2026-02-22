# Ansible modules for Warpgate

This directory contains Ansible modules to manage Warpgate resources, as well as the Python client for the Warpgate API.

## Structure

The code is organized in two parts, similar to the Terraform provider structure:

### Ansible Modules

The Ansible modules use the client package to provide idempotent resource management:

- `warpgate_user.py` - Module to manage users
- `warpgate_role.py` - Module to manage roles
- `warpgate_target.py` - Module to manage targets (SSH, HTTP, MySQL, PostgreSQL); target roles are managed via the `roles` list parameter on this module (not a separate module)
- `warpgate_password_credential.py` - Module to manage password credentials
- `warpgate_public_key_credential.py` - Module to manage SSH public key credentials
- `warpgate_user_role.py` - Module to manage user-role associations
- `warpgate_ticket.py` - Module to manage access tickets

## Usage

### Prerequisites

- Python 3.6+
- Ansible 2.9+
- Access to a Warpgate instance with an API token

### Configuration

All modules require the following parameters:

- `host` : Base URL of the Warpgate instance (e.g., `https://warpgate.example.com/@warpgate/admin/api/`)
- **Authentication** (one of):
  - `token` : Warpgate API authentication token
  - `api_username` and `api_password` : Warpgate admin credentials; the client will obtain a token automatically via the user API (POST /auth/login then POST /profile/api-tokens)

#### Obtaining an API token

- **Automatically (Ansible role):** If you use the full role and do not set `warpgate_api_token`, the role will try to obtain a token by calling `POST {{ warpgate_api_host }}session` with `warpgate_admin_username` and `warpgate_admin_password`. The response is expected to contain a `token`, `access_token`, or `api_token` field in JSON. If your Warpgate version uses a different login path or response shape, inspect the OpenAPI spec and adjust the task file `tasks/get_api_token.yml` accordingly.
- **Manually:** Create a token in the Warpgate Admin UI and set `warpgate_api_token` (e.g. in group_vars or extra vars).
- **Inspect the API:** To see available endpoints (e.g. session/login), fetch the OpenAPI spec from your instance:
  - Admin API: `curl -k https://localhost:8888/@warpgate/admin/api/openapi.json`
  - User API: `curl -k https://localhost:8888/@warpgate/api/openapi.json`

### Examples

#### Create a user

```yaml
- name: Create a Warpgate user
  warpgate_user:
    host: "https://warpgate.example.com"
    token: "{{ warpgate_api_token }}"
    username: "eugene"
    description: "Eugene - WarpGate Developer"
    credential_policy:
      http: ["Password", "Totp"]
      ssh: ["PublicKey"]
      mysql: ["Password"]
      postgres: ["Password"]
    state: present
```

#### Create a role

```yaml
- name: Create a Warpgate role
  warpgate_role:
    host: "https://warpgate.example.com"
    token: "{{ warpgate_api_token }}"
    name: "developers"
    description: "Role for development team"
    state: present
```

#### Create an SSH target (with roles)

Target roles are set via the `roles` list on `warpgate_target` (role IDs or names). Omit `roles` to leave existing roles unchanged; use an empty list to remove all roles.

```yaml
- name: Create an SSH target
  warpgate_target:
    host: "https://warpgate.example.com"
    token: "{{ warpgate_api_token }}"
    name: "app-server"
    description: "Application Server"
    ssh_options:
      host: "10.0.0.10"
      port: 22
      username: "admin"
      password_auth:
        password: "{{ ssh_password }}"
    roles:
      - "developers"
      - "database-admins"
    state: present
```

#### Assign a role to a user

```yaml
- name: Assign a role to a user
  warpgate_user_role:
    host: "https://warpgate.example.com"
    token: "{{ warpgate_api_token }}"
    user_id: "user-uuid"
    role_id: "role-uuid"
    state: present
```

#### Add an SSH public key

```yaml
- name: Add an SSH public key
  warpgate_public_key_credential:
    host: "https://warpgate.example.com"
    token: "{{ warpgate_api_token }}"
    user_id: "user-uuid"
    label: "Work Laptop"
    public_key: "ssh-rsa AAAAB3NzaC1yc2E... email@example.com"
    state: present
```

#### Create an access ticket

```yaml
- name: Create an access ticket
  warpgate_ticket:
    host: "https://warpgate.example.com"
    token: "{{ warpgate_api_token }}"
    username: "admin"
    target_name: "internal-web-app"
    state: present
  register: ticket_result

- name: Display the ticket secret
  ansible.builtin.debug:
    msg: "Ticket secret: {{ ticket_result.secret }}"
  when: ticket_result.secret is defined
```

## Python Client

The Python client (`warpgate_client/`) can be used independently of Ansible modules. It provides a simple interface to interact with the Warpgate API.

### Client usage example

```python
from ansible.module_utils.warpgate_client import WarpgateClient
from ansible.module_utils.warpgate_client.user import create_user, get_user
from ansible.module_utils.warpgate_client.role import create_role, add_user_role

client = WarpgateClient(
    host="https://warpgate.example.com",
    token="your-api-token"
)

# Create a user
user = create_user(client, "eugene", "Eugene - Developer")

# Create a role
role = create_role(client, "developers", "Development team")

# Assign the role to the user
add_user_role(client, user.id, role.id)
```

## Notes

- Modules support `check_mode` (dry-run)
- Password credentials cannot be read (API limitation)
- Tickets cannot be updated, only created or deleted
- Ticket secrets are only available at creation

## Compatibility

These modules are designed to work with Warpgate >= 0.13.2, inspired by the Terraform provider `terraform-provider-warpgate`.
