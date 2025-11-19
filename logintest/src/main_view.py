import flet as ft


class MainView:
    def __init__(self, page, user_id):
        self.page = page
        self.user_id = user_id
        self.content = None


    def build(self):
        user_id_text = ft.Text(
            f"User ID: {self.user_id}",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_400
        )

        # Web view container for z0r.de
        web_view = ft.WebView(
            url="https://z0r.de",
            expand=True,
            on_page_started=lambda e: print("Page started loading"),
            on_page_ended=lambda e: print("Page finished loading"),
        )

        # Main container
        main_container = ft.Container(
            content=ft.Column([
                # User ID section
                ft.Container(
                    content=user_id_text,
                    padding=20,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.Colors.GREY_300,
                        offset=ft.Offset(0, 2),
                    ),
                ),

                # Spacer
                ft.Container(height=20),

                # Web view container
                ft.Container(
                    content=web_view,
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.Colors.GREY_300,
                        offset=ft.Offset(0, 2),
                    ),
                ),
            ]),
            padding=20,
            expand=True,
        )

        self.content = main_container
        return self.content
