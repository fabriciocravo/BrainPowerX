from shiny import App, ui, render
from pathlib import Path

app_ui = ui.page_fluid(
    ui.h2("BrainPowerX"),
    ui.input_select(
        "cat",
        "Select a cat:",
        {"cat_1.png": "Cat 1", "cat_2.png": "Cat 2", "cat_3.png": "Cat 3"}
    ),
    ui.output_image("cat_image")
)

def server(input, output, session):
    @render.image
    def cat_image():
        return {"src": str(www_dir / "images" / input.cat()), "width": "400px"}

www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)