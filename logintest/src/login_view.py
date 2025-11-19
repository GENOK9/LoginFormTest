from typing import Optional
import flet as ft
import re
import webbrowser
from logintest.src.services.keycloak_service import KeycloakService
from services import db_service, login_handler

class LoginView:
    def __init__(self, page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.username_field = None
        self.password_field = None
        self.login_btn = None
        self.on_login_success = on_login_success
        self.keycloak_service = KeycloakService()

    def build(self) -> ft.Container:
        self.username_field = ft.TextField(
            label="username",
            hint_text="enter username here",
            color=ft.Colors.BLUE_400,
            border_color=ft.Colors.BLUE_400,
            width=300,
            autofocus=True,
            max_length=50,
            on_submit=lambda _: self.password_field.focus()
        )

        self.password_field = ft.TextField(
            label="password",
            hint_text="Enter password here",
            password=True,
            color=ft.Colors.RED_400,
            can_reveal_password=True,
            border_color=ft.Colors.BLUE_400,
            width=300,
            on_submit=lambda _: self._login_clicked(None)
        )

        self.login_btn = ft.ElevatedButton(
            text="Login",
            width=300,
            on_click=self._login_clicked,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_400,
            )
        )

        # Layout
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Login",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_400
                    ),
                    ft.Divider(height=20, color="transparent"),
                    self.username_field,
                    self.password_field,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row(
                        [self.login_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=20, color="transparent"),
                    ft.TextButton(
                        "Login with Keycloak",
                        on_click=lambda _: self.keycloak_clicked(None)                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            padding=40,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_300,
                offset=ft.Offset(0, 0),
            ),
        )

    def _login_clicked(self, e):
        email = self.username_field.value.strip()
        password = self.password_field.value

        is_valid, error_msg = self._validate_input(email, password)
        if not is_valid:
            print(error_msg)
            self.page.update()
            return

        try:
            success, user_id = self._login_user(email,password)
            if success and user_id:
                print("Login successful! Welcome back.")
                self.page.session.set("user_id", user_id)  # Session setzen
                self.password_field.value = ""
                self.on_login_success(user_id)
            else:
                print("Invalid credentials. Please try again.")
                self.password_field.value = ""

        except Exception as ex:
            print("An error occurred. Please try again later.")
            print(f"Exception: {ex}")

        finally:
            self.login_btn.disabled = False
            self.page.update()

    def _validate_input(self, email: str, password: str) -> tuple[bool, str]:
        # Client-side validation
        if not email or not password:
            return False, "Username and password are required"

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid input"

        return True, "Input valid"

    def _login_user(self, email: str, provided_password: str) -> tuple[bool, Optional[int]]:
       # Login attempt with optional Fake login for enumeration attacks
        lh = login_handler.LoginHandler()
        dbs = db_service.DBService()

        try:
            fetched_userpassword = dbs.fetch_user_password(email)

            if fetched_userpassword is None:
                # User doesn't exist - fake login
                lh.dummylogin(provided_password)
                return False, None

            stored_hash = fetched_userpassword[0]  # Passwort-Hash
            password_valid = lh.verify_password(provided_password, stored_hash)

            if not password_valid:
                return False, None

            user_id = self._get_user_id_by_email(email)
            return True, user_id

        except Exception as e:
            print(f"Login error: {e}")
            return False, None

    def _get_user_id_by_email(self, email: str) -> Optional[int]:
        #Fetch user_id AFTER Successful login
        try:
            dbs = db_service.DBService()
            user_data = dbs.fetch_user_id_by_email(email)  # Neue DB-Methode
            return user_data[0] if user_data else None
        except Exception as e:
            print(f"Error getting user_id: {e}")
            return None

    def keycloak_clicked(self, e):
        """Handle Keycloak OAuth2 login - opens browser"""
        try:
            # Get authorization URL
            auth_url = self.keycloak_service.get_auth_url()

            # Show message to user
            self.page.add(
                ft.SnackBar(
                    content=ft.Text("Opening browser for Keycloak login..."),
                    open=True
                )
            )
            self.page.update()

            # Open browser for OAuth2 flow
            webbrowser.open(auth_url)

            print(f"Opened browser with URL: {auth_url}")
            print("Please complete login in browser. You will be redirected back to the app.")

        except Exception as ex:
            print("An error occurred during Keycloak login.")
            print(f"Exception: {ex}")

# # Username field
# username_field = ft.TextField(
#     label="Username",
#     hint_text="Enter username here",
#     border_color=ft.Colors.BLUE_400,
#     width=300,
#     autofocus=True,
#     max_length=50,
#     on_submit=lambda _: password_field.focus()
# )
#
# # Password field
# password_field = ft.TextField(
#     label="Password",
#     hint_text="Enter password here",
#     password=True,
#     can_reveal_password=True,
#     border_color=ft.Colors.BLUE_400,
#     width=300,
#     on_submit=lambda _: login_clicked(None)
# )
#
#
# def login_clicked(e):
#     email = username_field.value.strip()
#     password = password_field.value
#
#     # Client-side validation
#     is_valid, error_msg = validate_input(email, password)
#     if not is_valid:
#         print(error_msg)
#         page.update()
#         return
#
#     # Show loading indicator
#     loading.visible = True
#     login_btn.disabled = True
#     page.update()
#
#     # Attempt login
#     try:
#         success, user_id = _login_user(email, password)
#         if success and user_id:
#             print("Login successful! Welcome back.")
#             page.session.set("user_id", user_id)  # Session setzen
#             password_field.value = ""
#             page.go("/app")
#         else:
#             print("Invalid credentials. Please try again.")
#             password_field.value = ""
#
#
#     except Exception as ex:
#         print("An error occurred. Please try again later.")
#         print(f"Exception: {ex}")
#
#     finally:
#         # Hide loading indicator
#         loading.visible = False
#         login_btn.disabled = False
#         page.update()
#
#
# # Loading indicator
# loading = ft.ProgressRing(visible=False, width=20, height=20)
#
#
# def validate_input(email: str, password: str) -> tuple[bool, str]:
#     """Client-side validation before sending to server"""
#     if not email or not password:
#         return False, "Username and password are required"
#
#     # Basic sanitization check
#     if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#             , email):
#         return False, "wrong credentials"
#
#     return True, "login success"