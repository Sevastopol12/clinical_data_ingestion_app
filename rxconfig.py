import reflex as rx

config = rx.Config(
    app_name="data_managment_system",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                accent_color="violet",
                appearance="dark",
                has_background=True,
            ),
        ),
    ],
)
