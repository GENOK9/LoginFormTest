from keycloak import KeycloakOpenID
import os
import webbrowser
import urllib.parse
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class KeycloakService:
    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=os.getenv("KEYCLOAK_SERVER_URL"),  # e.g., "http://localhost:8080/"
            client_id=os.getenv("KEYCLOAK_CLIENT_ID"),    # e.g., "your-client-id"
            realm_name=os.getenv("KEYCLOAK_REALM"),       # e.g., "your-realm"
            client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET")  # Optional
        )
        self.redirect_uri = os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:49301/callback")

    def get_auth_url(self) -> str:
        """Get the authorization URL for OAuth2 flow"""
        return self.keycloak_openid.auth_url(
            redirect_uri=self.redirect_uri,
            scope="openid profile email"
        )

    def exchange_code_for_token(self, authorization_code: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Exchange authorization code for access token
        Returns (success: bool, user_info: dict or None)
        """
        try:
            # Exchange code for token
            token = self.keycloak_openid.token(
                grant_type='authorization_code',
                code=authorization_code,
                redirect_uri=self.redirect_uri
            )

            # Get user info
            user_info = self.keycloak_openid.userinfo(token['access_token'])

            return True, {
                'access_token': token['access_token'],
                'refresh_token': token['refresh_token'],
                'username': user_info.get('preferred_username'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'user_info': user_info
            }

        except Exception as e:
            print(f"Token exchange error: {e}")
            return False, None

    def validate_token(self, access_token: str) -> bool:
        """Validate if token is still valid"""
        try:
            user_info = self.keycloak_openid.userinfo(access_token)
            return user_info is not None
        except Exception:
            return False