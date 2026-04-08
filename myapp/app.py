import numpy as np
from numba.core.types import double
from numba.parfors.array_analysis import MAP_TYPES
from shiny import App, ui, render, reactive
from data_utils.utils import *
from pathlib import Path
import json

# ---------------------------------------------------------------------------
# Load index and derive filter options from folder names
# Folder name format: {dataset}_{map_type}_{task}_{test_type}
# e.g. hcp_fc_REST_EMOTION_t
# ---------------------------------------------------------------------------

METHODS = [
    "Constrained_FDR",
    "Constrained_FWER",
    "Fast_TFCE",
    "Parametric_FDR",
    "Parametric_FWER",
    "Size",
]

BASE_DIR = Path(__file__).parent

DATASETS, MAP_TYPES, TASKS, SAMPLE_SIZES = (
    compile_options(BASE_DIR / "data_utils" / "menu_options.json")
)

INDEX = get_index(BASE_DIR / "results" / "data_base_index.json")

# SAMPLE_SIZES = [20, 40, 80, 120, 200]

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h5("Dataset"),
        ui.input_selectize(
            "dataset", None,
            choices=DATASETS,
            multiple=True,
            options={"placeholder": "All datasets"},
        ),

        ui.hr(),
        ui.h5("Map Type"),
        ui.input_selectize(
            "map_type", None,
            choices=MAP_TYPES,
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
        ui.h5("Sample Size"),
        ui.input_text(
            "n_subjects", None,
            placeholder="e.g. 20  or  20, 80, 120",
            value="",
        ),

        ui.hr(),
        ui.h5("Methods"),
        ui.input_selectize(
            "methods", None,
            choices=METHODS,
            multiple=True,
            options={"placeholder": "All methods"},
        ),

        width=260,
        bg="#f8f8f8",
    ),

    # ------------------------------------------------------------------
    # Main panel — placeholder until next step
    # ------------------------------------------------------------------
    ui.output_ui("main_panel"),
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

        data_set_results = []
        for d in list(input.dataset()):
            data_set_results = data_set_results + INDEX[d.lower()]
        data_set_results = set(data_set_results)

        map_results = []
        for m in list(input.map_type()):
            map_results = map_results + INDEX[m.lower()]
        map_results = set(map_results)

        task_results = []
        for t in list(input.task()):
            task_results =  task_results + INDEX[t.lower()]
        task_results = set(task_results)

        results = data_set_results & map_results & task_results
        results = sorted(list(results))

        if not results:
            results = INDEX["hcp"] # Return hcp plots as default

        return results

    # ── Active methods (empty selection → all) ───────────────────────────
    @reactive.Calc
    def active_methods():
        sel = list(input.methods())
        return sel if sel else None

    # ── Main panel: just echo selections for now ─────────────────────────
    @output
    @render.ui
    def main_panel():
        folders = matched_folders()
        sizes   = selected_sizes()
        methods = active_methods()

        if not folders:
            return ui.p("No experiments match the current filters.",
                        style="color:gray; padding:1rem;")

        return ui.div(
            ui.h4(f"{len(folders)} experiment(s) matched"),
            ui.tags.ul(*[ui.tags.li(f) for f in folders]),
            ui.p(f"Sample sizes: {sizes}"),
            ui.p(f"Methods: {methods}"),
        )

app = App(app_ui, server)