"""
teams.py — send a 1:1 Teams chat message via Microsoft Graph using client credentials.

Required `.env` variables:
- TEAMS_CLIENT_ID
- TEAMS_CLIENT_SECRET
- TEAMS_TENANT_ID
- TEAMS_RECIPIENT_UPN
- (optional) TEAMS_SENDER_UPN
- (optional) TEAMS_DEFAULT_MESSAGE

Usage:
    python teams.py                  # sends TEAMS_DEFAULT_MESSAGE
    python teams.py "Custom message"   # sends the provided message

Notes:
- The Azure AD app requires admin consent for application Graph permissions that allow creating chats and sending messages.
- If running into permission errors, confirm the app has been granted the required Graph application permissions and admin consent has been granted.
"""

import os
import sys
import requests
import urllib.parse
from dotenv import load_dotenv
import msal

GRAPH_RESOURCE = "https://graph.microsoft.com/"
GRAPH_SCOPE = [GRAPH_RESOURCE + ".default"]


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret,
    )
    result = app.acquire_token_for_client(scopes=GRAPH_SCOPE)
    if "access_token" in result:
        return result["access_token"]
    raise RuntimeError(f"Could not obtain access token: {result}")


def get_delegated_token(tenant_id: str, client_id: str, scopes: list) -> str:
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.PublicClientApplication(client_id, authority=authority)
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise RuntimeError(f"Failed to initiate device flow: {flow}")
    # Print instructions to the terminal for the user to authenticate
    print(flow["message"])  # contains URL and user code
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        return result["access_token"]
    raise RuntimeError(f"Failed to acquire token by device flow: {result}")


def get_user_id(access_token: str, user_upn: str) -> str:
    # Use the user principal name directly in the users/{id|userPrincipalName} path.
    # URL-encode the UPN to support characters like '#' (external guest accounts):
    encoded_upn = urllib.parse.quote(user_upn, safe='')
    url = GRAPH_RESOURCE + "v1.0/users/" + encoded_upn
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("id")
    raise RuntimeError(f"Failed to resolve user '{user_upn}': {resp.status_code} {resp.text}")


def create_chat(access_token: str, sender_id: str, recipient_id: str) -> str:
    url = GRAPH_RESOURCE + "v1.0/chats"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{sender_id}')"
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{recipient_id}')"
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in (201, 200):
        return resp.json().get("id")
    raise RuntimeError(f"Failed to create chat: {resp.status_code} {resp.text}")


def send_chat_message(access_token: str, chat_id: str, message: str) -> dict:
    url = GRAPH_RESOURCE + f"v1.0/chats/{chat_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"body": {"contentType": "html", "content": message}}
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in (201, 200):
        return resp.json()
    raise RuntimeError(f"Failed to send message: {resp.status_code} {resp.text}")


def main():
    try:
        load_dotenv()

        client_id = os.getenv("TEAMS_CLIENT_ID")
        client_secret = os.getenv("TEAMS_CLIENT_SECRET")
        tenant_id = os.getenv("TEAMS_TENANT_ID")
        sender_upn = os.getenv("TEAMS_SENDER_UPN")
        recipient_upn = os.getenv("TEAMS_RECIPIENT_UPN")
        default_message = os.getenv("TEAMS_DEFAULT_MESSAGE", "Hello from ACS Lab")
        auth_mode = os.getenv("TEAMS_AUTH_MODE", "app").lower()

        if not all([client_id, client_secret, tenant_id, recipient_upn]):
            raise ValueError("Missing one or more required TEAMS_ environment variables. See .env for stubs.")

        # Choose authentication method based on auth mode
        if auth_mode == "delegated":
            # Delegated flow requires the app have delegated Graph permissions.
            # Request User.Read.All so the signed-in user can resolve other users by UPN.
            scopes = ["User.Read.All", "Chat.ReadWrite"]
            access_token = get_delegated_token(tenant_id, client_id, scopes)
        else:
            access_token = get_access_token(tenant_id, client_id, client_secret)

        # Resolve user ids
        if sender_upn:
            sender_id = get_user_id(access_token, sender_upn)
        else:
            print("No TEAMS_SENDER_UPN set; the application will create the chat on behalf of the app if permitted.")
            sender_id = None

        recipient_id = get_user_id(access_token, recipient_upn)

        # If sender_id is provided, create a chat with both users; otherwise try to create a chat with just the recipient
        if sender_id:
            chat_id = create_chat(access_token, sender_id, recipient_id)
        else:
            # Attempt to create a one-on-one chat where the app is implicitly the initiator. This requires application-level permissions.
            chat_id = create_chat(access_token, recipient_id, recipient_id)

        message_text = default_message
        # allow override via CLI arg
        if len(sys.argv) > 1:
            message_text = sys.argv[1]

        result = send_chat_message(access_token, chat_id, message_text)
        print("Message sent. Message id:", result.get("id"))

    except Exception as ex:
        print("Error:", ex)


if __name__ == "__main__":
    main()