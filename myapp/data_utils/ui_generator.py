from click import style
from shiny import App, ui, render, reactive
from pathlib import Path
import json
import re
from .utils import method_display_name

def power_heatmap_card(id: str, BASE_DIR: Path) -> ui.layout_columns:
    """
    :param id: id is the folder indentification, the folder name itself
    :return: the ui for shiny
    """

    # Find available sample
    path_to_element = BASE_DIR / 'results' / id

    metadata = json.loads((path_to_element / "metadata.json").read_text())
    sample_sizes = metadata["sample_sizes"]
    methods = metadata["methods"]

    return ui.div(

        # --- Left: Power curves ---
        ui.card(
            ui.card_header("Power curves"),
            ui.layout_columns(
                ui.output_image(f"{id}_curve_img", inline=True),
                ui.input_radio_buttons(
                    f"{id}_curve_type",
                    label=None,
                    choices={
                        "average": "Average",
                        "n20":     "n > 20%",
                        "n50":     "n > 50%",
                        "n80":     "n > 80%",
                    },
                    selected="average",
                ),
                col_widths=[9, 3],
                style="width: 100%;"
            ),
        ),

        # --- Right: Heatmaps ---
        ui.card(
            ui.card_header("Heatmaps"),
            ui.layout_columns(
                ui.output_image(f"{id}_heatmap_img", inline=True),
                ui.div(
                    ui.input_selectize(
                        f"{id}_subjects",
                        "Subjects",
                        choices=[str(n) for n in sample_sizes], # I need to fix this
                    ),
                    ui.input_selectize(
                        f"{id}_method",
                        "Method",
                        choices={m: method_display_name(m) for m in methods},
                    ),
                ),
                col_widths=[9, 3],
                style="width: 100%;"
            ),
        ),

        # col_widths=[6, 6],
        style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; width: 100%;"
    )





