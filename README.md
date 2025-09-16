# ACS Lab — Email, SMS, and Teams messaging

This repository contains small example scripts that demonstrate sending messages via Azure Communication Services and Microsoft Teams. The code and environment variables were implemented and tested during an interactive session. This README documents the exact setup steps so the work can be repeated in another environment.

Files
- `mail.py` — sends an email using Azure Communication Services Email SDK (app-only, connection string from `.env`).
- `sms.py` — sends an SMS using Azure Communication Services SMS SDK (app-only, connection string from `.env`).
- `teams.py` — sends a 1:1 Teams chat message. Supports two auth modes:
  - `app` (client credentials) — application permissions
  - `delegated` (device-code) — interactive user sign-in (used for the smoke tests)
- `.env` — environment configuration (do NOT commit secrets)

Prerequisites
1. Python 3.8+ in your environment.
2. An Azure subscription and an EntraID tenant.
3. An Azure Communication Service resource for Email and SMS (if you want to run those samples).
4. An EntraID app registration for Microsoft Graph access (for Teams messaging).

Install dependencies

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install python-dotenv msal requests azure-communication-email azure-communication-sms
```

Environment configuration (`.env`)

Create a `.env` at the repository root with the following keys (exact names used by the scripts):

```
# Email (Azure Communication Services)
CONNECTION_STRING_EMAIL="<acs-email-connection-string>"
SENDER_ADDRESS="sender@yourdomain"
RECIPIENT_ADDRESS="recipient@yourdomain"

# SMS (Azure Communication Services)
CONNECTION_STRING_SMS="<acs-sms-connection-string>"
SMS_FROM="+1XXXXXXXXXX"
SMS_TO="+1YYYYYYYYYY"

# Teams / Microsoft Graph
TEAMS_CLIENT_ID="<app-client-id>"
TEAMS_CLIENT_SECRET="<client-secret>"   # needed for app-only mode
TEAMS_TENANT_ID="<tenant-id>"
TEAMS_SENDER_UPN="sender@yourtenant.onmicrosoft.com"
TEAMS_RECIPIENT_UPN="recipient@yourtenant.onmicrosoft.com"
TEAMS_DEFAULT_MESSAGE="Hello from ACS Lab"
# Set to delegated to use device-code flow for an interactive user sign-in
# TEAMS_AUTH_MODE="delegated"
```

Important: never commit `.env` or secrets to source control. Add `.env` to `.gitignore`.

EntraID app registration and Graph permissions (executed during the session)

1. Create an app registration at `EntraID > App registrations > New registration`.
2. Note the **Application (client) ID** and **Directory (tenant) ID** — copy into `.env`.
3. Under **Certificates & secrets** create a **Client secret** and copy the *value* into `.env` (only shown once).
4. Under **API permissions** add Microsoft Graph permissions:
   - Application permissions (if you want app-only flows): `Chat.Create`, `Chat.ReadWrite.All`, `User.Read.All` (admin consent required)
   - Delegated permissions (for device-code / delegated flows): `Chat.ReadWrite`, `User.Read.All` or `User.ReadBasic.All`, `User.Read` (as needed)
5. Click **Grant admin consent** (Global Administrator required). If you are testing delegated device code flow, also enable **Allow public client flows**: `Authentication > Advanced settings > Allow public client flows = Yes`.

Why two auth modes?
- App-only (client credentials): allows automated services to operate without user interaction. Some Graph chat APIs are restricted or require special privileges; app-only creation of 1:1 chats and sending messages is limited in some tenants and may require additional roles (e.g., migration privileges).
- Delegated (device code): the script prompts for a user sign-in and performs actions on behalf of that user. This approach is simpler for testing message sending and does not require special migration permissions.

How to run the samples

- Email: `python mail.py`
- SMS: `python sms.py`
- Teams (app-only): set `TEAMS_AUTH_MODE` unset or `app`, ensure application permissions and client secret are configured, then `python teams.py`
- Teams (delegated/device-code): set `TEAMS_AUTH_MODE="delegated"` in `.env`, run `python teams.py`, follow the printed https://microsoft.com/devicelogin URL and enter the displayed code to authenticate.
- To send a custom message: `python teams.py "Custom message here"`

Testing steps we completed in the session
1. Moved connection strings and addresses to `.env` for `mail.py` and `sms.py`.
2. Implemented `teams.py`, initially using app-only auth.  
   - Encountered permission and chat-creation restrictions for app-only mode.
3. Added delegated device-code flow to `teams.py` and adjusted delegated scopes to request `User.Read.All` and `Chat.ReadWrite` so the signed-in user could resolve other users and send messages.
4. Enabled **Allow public client flows** in the app registration to allow the device-code flow.
5. Ran delegated smoke tests (device-code authentication) and verified message delivery. Message IDs were printed to the console for verification.
6. Demonstrated swapping sender/recipient values in `.env` and re-running the smoke test.

Troubleshooting notes
- `invalid_client` with description `Invalid client secret ...` → you copied the *secret id* rather than the secret *value*. Create a new client secret and paste its value.
- `Not granted for <Tenant>` → grant admin consent to the requested Graph permissions (Global Admin required).
- `Duplicate chat members` → chat creation failed because both chat members were identical; ensure `TEAMS_SENDER_UPN` and `TEAMS_RECIPIENT_UPN` are different.
- `Authorization_RequestDenied` when reading users with delegated token → add and grant `User.Read.All` or `User.ReadBasic.All` delegated permission and re-authenticate.

Security and production notes
- Do not store secrets in source control. Use a secure secret store (Azure Key Vault, environment variables set in CI/CD) in production.
- Device-code flow is intended for interactive testing; for headless production scenarios consider server-to-server flows only after validating Graph API support and required permissions.
- Review and limit application permissions: `Chat.*` and `User.*` application permissions are powerful; ensure admin approvals and an appropriate security review.

Appendix: Useful commands
- Install packages: `pip install python-dotenv msal requests azure-communication-email azure-communication-sms`
- Run a script: `python teams.py "optional message"`

If you'd like, I can add a `requirements.txt` and a small `CONTRIBUTING.md` with the minimal checklist for a new environment. Which would you prefer next?