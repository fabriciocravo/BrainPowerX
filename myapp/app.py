from dbm.sqlite3 import error

import numpy as np
from seaborn import heatmap
from shiny import App, ui, render, reactive
from shiny.ui import input_selectize
from torch.onnx.symbolic_opset9 import contiguous

from data_utils.ui_generator import power_heatmap_card
from data_utils.menu_options import OPTIONS
from data_utils.css import _CSS
import data_utils.utils as utils
from pathlib import Path
import json

# ---------------------------------------------------------------------------
# Load index and derive filter options from folder names
# Folder name format: {dataset}_{map_type}_{task}_{test_type}
# e.g. hcp_fc_REST_EMOTION_t
# ---------------------------------------------------------------------------


BASE_DIR = Path(__file__).parent

DATASETS, MAP_TYPES, TASKS, SAMPLE_SIZES, METHODS, CURVE_CHOICE = (
    utils.compile_options(OPTIONS)
)

INDEX = utils.get_index(BASE_DIR / "results" / "data_base_index.json")

ui_card_list = []

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.style(_CSS)),

    # ── Full-width header above everything ────────────────────────────────────
    ui.div(
        ui.div(
            ui.tags.img(src="static/neuroprism_logo.png", class_="bpx-logo"),
            ui.div(
                ui.tags.h1("BrainPowerX"),
                ui.tags.p("Statistical power calculator for neuroimaging studies"),
                class_="bpx-title-block",
            ),
            class_="bpx-header-left",
        ),
        ui.div(
            ui.tags.img(src="static/neuroprism_logo.png", style="height:42px; width:auto; opacity:0.7;"),
            ui.tags.span("The NeuroPrism Lab"),
            class_="bpx-lab-badge",
        ),
        class_="bpx-header",
    ),

    ui.div(
        # Sidebar panel
        ui.div(
            ui.h5("Dataset"),
            ui.input_selectize(
                "dataset", None,
                choices=DATASETS,
                selected=["HPC"],
                multiple=True,
                options={"placeholder": "All datasets"},
            ),
            ui.hr(),
            ui.h5("Map Type"),
            ui.input_selectize(
                "map_type", None,
                choices=MAP_TYPES,
                selected=["FC"],
                multiple=True,
                options={"placeholder": "fc / activation"},
            ),
            ui.hr(),
            ui.h5("Study type"),
            ui.input_selectize(
                "task", None,
                choices=TASKS,
                multiple=True,
                options={"placeholder": "All tasks"},
            ),
            ui.hr(),
            ui.h5("Methods"),
            ui.input_selectize(
                "methods", None,
                choices=METHODS,
                multiple=False,
                selected="Parametric_FWER",
                options={"placeholder": "All methods"},
            ),
            ui.hr(),
            ui.h5("Curve Choice"),
            ui.input_selectize(
                "curve_choice", None,
                choices=CURVE_CHOICE,
                multiple=False,
                options={"placeholder": "Average"},
            ),
            ui.hr(),
            ui.h5("Sample Size"),
            ui.input_text(
                "n_subjects", None,
                placeholder="e.g. 20  or  20, 80, 120",
                value="200",
            ),
            ui.hr(),
            ui.h5("Desired Power"),
            ui.input_text(
                "desired_power", None,
                placeholder="e.g. 80",
                value="80",
            ),
            class_="sidebar-panel",
        ),
        # Main panel
        ui.div(
            ui.output_ui(
                "main_panel",
                fill=True,
                fillable=True,
            ),
            class_="main-panel",
        ),
        class_="app-layout",
    ),
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):

    # ── Parse the free-text sample-size field ───────────────────────────
    @reactive.Calc
    def selected_sizes():
        raw = input.n_subjects().strip()
        if not raw:
            return None                         # empty → all sizes

        try:
            first_size = int(raw.replace(",", " ").split()[0])
        except:
            raise ValueError("Sample size could not be converted to number")

        previous_error = np.inf
        for (i, n_sub) in enumerate(SAMPLE_SIZES):

            error = (n_sub - first_size)**2
            if error > previous_error:
                return SAMPLE_SIZES[i - 1] # Array is sorted, if error got worse, return previous
            else:
                previous_error = error

        # Return last, best possible error
        return SAMPLE_SIZES[-1]


    # ── Intersect index to find matching result folders ─────────────────
    @reactive.Calc
    def matched_folders():

        def input_lookup(multiple_selection_input):

            return_set = set()
            for key in multiple_selection_input:
                return_set |= index_lookup(INDEX, key)

            return return_set

        def index_lookup(index, key):

            result_from_query = set()
            if key not in index:
                pass
            else:
                result_from_query |= set(index[key])

            return result_from_query

        data_set_results = input_lookup(input.dataset())

        map_results =  input_lookup(input.map_type())

        # I should consider that tasks have multiple different names
        # Selectors must match all

        set_tasks = set()
        for task in input.task():
            t_list = utils.task_map_names(task)
            set_tasks |= input_lookup(t_list)

        results = data_set_results & map_results & set_tasks
        results = sorted(list(results))

        if not results:
            results = INDEX["HCP"] # Return hcp plots as default

        return results

    # ── Active methods (empty selection → all) ───────────────────────────
    @reactive.Calc
    def active_methods():
        sel = list(input.methods())
        return sel if sel else None

    # ── Main panel: just echo selections for now ─────────────────────────
    @render.ui
    def main_panel():
        return ui.div(
                    *[power_heatmap_card(f, BASE_DIR) for f in matched_folders()],
                    style="width: 100%;",
               )

    def register_card_outputs(folder_name: str):

        # Register the image output
        @output(id=f"{folder_name}_curve_img")
        @render.image
        def _():
            path_power_img = BASE_DIR / "results" / f"{folder_name}"
            curve_choice = input.curve_choice()

            if 'average' in curve_choice.lower():
                path_power_img = path_power_img / 'average_power_curves.png'
            elif '20' in curve_choice:
                path_power_img = path_power_img / 'edges_above_threshold_20.png'
            elif '50' in curve_choice:
                path_power_img = path_power_img / 'edges_above_threshold_50.png'
            elif '80' in curve_choice:
                path_power_img = path_power_img / 'edges_above_threshold_80.png'
            else:
                raise TypeError('Power image type not correct recognized from options')

            return  {"src": str(path_power_img), "alt": f"{folder_name}_curve_img"}

        # Register the heatmap output
        @output(id=f"{folder_name}_heatmap_img")
        @render.image
        def _():

            heatmap_img_path = BASE_DIR / "results" / f"{folder_name}"

            # Handling subject number
            n_subs = input.n_subjects()
            method = input.methods()

            heatmap_json_path = heatmap_img_path / "metadata.json"

            with open(heatmap_json_path) as f:
                meta_json = json.load(f)
                sub_list = meta_json["sample_sizes"]

            if not n_subs:
                n_subs = 'n' + str(sub_list[-1])
            else:
                n = int(input.n_subjects())

                for i in range(1, len(sub_list)):
                    if (sub_list[i - 1] - n) ** 2 < (sub_list[i] - n) ** 2:
                        n_subs = 'n' + str(sub_list[i - 1])
                        break
                else:
                    n_subs = 'n' + str(sub_list[-1])

            heat_map_img_name = "heatmap_" + method + '_' + n_subs + '.png'

            heatmap_img_path = heatmap_img_path / heat_map_img_name

            return {"src": str(heatmap_img_path), "alt": f"{folder_name}_heatmap_img"}

    @reactive.effect
    def _register_outputs():
        for folder_name in matched_folders():
            register_card_outputs(folder_name)



app = App(app_ui, server, static_assets={"/static": BASE_DIR / "static"})

if __name__ == '__main__':

    pass

