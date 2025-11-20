import flet as ft
import urllib.parse

from login_view import LoginView
from main_view import MainView
from services.keycloak_service import KeycloakService

def main(page: ft.Page):
    page.title = "logintest"
    keycloak_service = KeycloakService()

    def route_change(e):
        page.views.clear()

        if page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.Container(
                            content=LoginView(page, on_login_success=lambda user: page.go("/app")).build(),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    ],
                )
            )
            page.update()

        # HANDLE KEYCLOAK CALLBACK
        elif page.route.startswith("/callback"):
            print("=== KEYCLOAK CALLBACK DETECTED ===")
            handle_keycloak_callback(page.route)

        # MAIN APP VIEW
        elif page.route == "/app":
            user_id = page.session.get("user_id")
            keycloak_user = page.session.get("keycloak_user")

            # Use whichever is available
            display_user = keycloak_user if keycloak_user else user_id

            if not display_user:
                # No valid session, redirect to login
                print("No valid session, redirecting to login")
                page.go("/login")
                return

            page.views.append(
                ft.View(
                    "/app",
                    [
                        ft.AppBar(
                            title=ft.Text("Flexibler Schreibtisch"),
                            actions=[
                                ft.IconButton(
                                    icon=ft.Icons.SETTINGS,
                                    on_click=lambda _: page.go("/settings")
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.LOGOUT,
                                    on_click=lambda _: logout()
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.HELP_CENTER,
                                    on_click=lambda _: page.go("/test")
                                )
                            ]
                        ),
                        MainView(page, display_user).build()
                    ]
                )
            )
            page.update()

    def handle_keycloak_callback(route: str):
        """Handle Keycloak OAuth2 callback"""
        print(f"=== KEYCLOAK CALLBACK DEBUG ===")
        print(f"Full callback route: {route}")

        try:
            # Parse URL parameters
            if "?" in route:
                query_string = route.split("?")[1]
                params = urllib.parse.parse_qs(query_string)

                if "code" in params:
                    authorization_code = params["code"][0]
                    print(f"Authorization code: {authorization_code}")

                    # Show loading
                    page.views.append(
                        ft.View(
                            "/callback",
                            [
                                ft.Container(
                                    content=ft.Column([
                                        ft.ProgressRing(),
                                        ft.Text("Processing login...")
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    alignment=ft.alignment.center,
                                    expand=True
                                )
                            ]
                        )
                    )
                    page.update()

                    # Exchange code for token
                    success, user_data = keycloak_service.exchange_code_for_token(authorization_code)

                    if success and user_data:
                        print(f"Keycloak login successful! Welcome {user_data['username']}")

                        # Store user data in session
                        page.session.set("keycloak_user", user_data['username'])
                        page.session.set("keycloak_token", user_data['access_token'])
                        page.session.set("keycloak_refresh_token", user_data['refresh_token'])

                        # Redirect to main app
                        page.go("/app")
                    else:
                        print("Failed to exchange authorization code")
                        page.go("/login")

                elif "error" in params:
                    error = params["error"][0]
                    print(f"OAuth error: {error}")
                    page.go("/login")
                else:
                    print("No authorization code in callback")
                    page.go("/login")
            else:
                print("Invalid callback URL")
                page.go("/login")

        except Exception as e:
            print(f"Callback handling error: {e}")
            page.go("/login")

    def logout():
        page.session.clear()
        page.go("/login")

    page.on_route_change = route_change
    page.go("/login")

ft.app(target=main)