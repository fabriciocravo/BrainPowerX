from click import style
from google.genai.types import Outcome
from shiny import App, ui, render, reactive
from pathlib import Path
import json
import re
from .utils import method_display_name

def power_heatmap_card(name: str, BASE_DIR: Path) -> ui.layout_columns:
    """
    :param name: id is the folder indentification, the folder name itself
    :return: the ui for shiny
    """

    # Find available sample
    path_to_element = BASE_DIR / 'results' / name

    metadata = json.loads((path_to_element / "metadata.json").read_text())
    outcome = metadata["outcome"]

    return ui.div(
        ui.card(
            ui.card_header(f"Power Data - {outcome}"),
            ui.layout_columns(
                ui.output_text_verbatim(f"{name}_calculation_text"),
                ui.output_image(f"{name}_curve_img", inline=True),
                ui.output_image(f"{name}_heatmap_img", inline=True),
                col_widths=[4, 4, 4],
            ),
        )
    )





