import numpy as np
from shiny import App, ui, render, reactive

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
"""
    Todo:
    - Change figures, put legend outside the main image
    - HCP first
"""

BASE_DIR = Path(__file__).parent

DATASETS, MAP_TYPES, OUTCOMES, TEST_TYPES, SAMPLE_SIZES, METHODS, CURVE_CHOICE = (
    utils.compile_options(OPTIONS)
)

INDEX = utils.get_index(BASE_DIR / "results" / "data_base_index.json")

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
                selected=["HCP"],
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
            ui.h5("Outcomes"),
            ui.input_selectize(
                "outcomes", None,
                choices=OUTCOMES,
                multiple=True,
                options={"placeholder": "All outcomes"},
            ),
            ui.h5("Test Types"),
            ui.input_selectize(
                "test_types", None,
                choices=TEST_TYPES,
                multiple=True,
                options={"placeholder": "All tests"},
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
                selected="Average",
                options={"placeholder": "Average"},
            ),
            ui.hr(),
            ui.h5("Desired Power or Sample Size"),
            ui.input_select(
                "analysis_mode", None,
                choices={
                    "desired_power": "Desired power → Est. Subjects",
                    "n_subjects": "Sample size → Est. Power",
                },
                selected="desired_power",
            ),
            ui.hr(),
            ui.h5("Analysis Value (Desired Power or Sample Size)"),
            ui.input_text(
                "analysis_value", None,
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

        if input.dataset():
            data_set_results = input_lookup(input.dataset())
        else:
            data_set_results = input_lookup(DATASETS)

        if input.map_type():
            map_results = input_lookup(input.map_type())
        else:
            map_results = input_lookup(MAP_TYPES)

        # I should consider that tasks have multiple different names
        # Selectors must match all
        # Both set and tasks must search for all related if none is selected
        set_outcomes = set()
        if input.outcomes():
            for outcome in input.outcomes():
                o_list = utils.outcome_map_names(outcome)
                set_outcomes |= input_lookup(o_list)
        else:
            for outcome in OUTCOMES:
                o_list = utils.outcome_map_names(outcome)
                set_outcomes  |= input_lookup(o_list)

        if input.test_types():
            set_test_types = input_lookup(input.test_types())
        else:
            set_test_types = input_lookup(TEST_TYPES)

        results = data_set_results & map_results & set_outcomes & set_test_types
        # Sort according to correct dataset
        DATASET_SORT_ORDER = {dataset: i for i, dataset in enumerate(["HCP", "UKB", "ABCD"])}

        def dataset_sort_key(folder_name):
            for dataset, rank in DATASET_SORT_ORDER.items():
                if dataset in folder_name:
                    return rank
            return len(DATASET_SORT_ORDER)

        results = sorted(list(results), key=dataset_sort_key)

        if not results:
            results = INDEX["HCP"] # Return hcp plots as default

        return results

    # ── Main panel: just echo selections for now ─────────────────────────
    @render.ui
    def main_panel():
        return ui.div(
                    *[power_heatmap_card(f, BASE_DIR) for f in matched_folders()],
                    style="width: 100%;",
               )

    def register_card_outputs(folder_name: str):

         # Calculate acording to user based input
        @reactive.Calc
        def card_analysis():
            metadata_path = BASE_DIR / "results" / f"{folder_name}" / "metadata.json"
            with open(metadata_path) as f:
                metadata = json.load(f)

            curve_choice = input.curve_choice()
            if 'average' in curve_choice.lower():
                type_of_curve = "power_curve_fits"
            elif '20' in curve_choice:
                type_of_curve = "p20"
            elif '50' in curve_choice:
                type_of_curve = "p50"
            elif '80' in curve_choice:
                type_of_curve = "p80"
            else:
                raise TypeError('Power image type not correctly recognized from options')

            method = input.methods()
            analysis_mode = input.analysis_mode()
            analysis_value = float(input.analysis_value())

            P, a, b = utils.get_result_value_from_meta_data(metadata, type_of_curve, method)

            estimation = utils.find_estimation_of_desired_value(
                analysis_value, analysis_mode, P, a, b
            )

            return {
                "metadata": metadata,
                "type_of_curve": type_of_curve,
                "method": method,
                "P": P,
                "a": a, 
                "b": b,
                "estimation": estimation,
                "analysis_mode": analysis_mode,
                "analysis_value": analysis_value,
            }
        
        # Register the image output
        @output(id=f"{folder_name}_curve_img")
        @render.image
        def _():
            path_power_img = BASE_DIR / "results" / f"{folder_name}"
            c_data = card_analysis()
            type_of_curve = c_data["type_of_curve"]

            if type_of_curve == 'power_curve_fits':
                path_power_img = path_power_img / 'average_power_curves.png'
            elif type_of_curve == 'p20':
                path_power_img = path_power_img / 'edges_above_threshold_20.png'
            elif type_of_curve == 'p50':
                path_power_img = path_power_img / 'edges_above_threshold_50.png'
            elif type_of_curve == 'p80':
                path_power_img = path_power_img / 'edges_above_threshold_80.png'
            else:
                raise TypeError('Power image type not correct recognized from options')

            return  {"src": str(path_power_img), "alt": f"{folder_name}_curve_img"}

        @output(id=f"{folder_name}_heatmap_img")
        @render.image
        def _():
            # Extract necessary data for heatmap
            c_data = card_analysis()
            method = c_data['method']
            sub_list = c_data['metadata']['sample_sizes']
            analysis_mode = c_data['analysis_mode']

            if utils.non_heatmap_methods(method):
                return None

            if analysis_mode == 'n_subjects':
                desired_subs = c_data['analysis_value']
            elif analysis_mode == 'desired_power':
                desired_subs = c_data['estimation']
            else:
                raise ValueError('Analysis mode not supported')

            closest = min(sub_list, key=lambda n: (n - desired_subs) ** 2)
            n_subs = 'n' + str(closest)

            heatmap_img_path = BASE_DIR / "results" / folder_name / f"heatmap_{method}_{n_subs}.png"
            return {"src": str(heatmap_img_path), "alt": f"{folder_name}_heatmap_img"}

        @output(id=f"{folder_name}_calculation_text")
        @render.text
        def _():
            # Get necessary data from card
            c_data = card_analysis()
            type_of_curve = c_data['type_of_curve']
            method = c_data['method']
            sub_list = c_data['metadata']['sample_sizes']
            metric = "power" if type_of_curve == "power_curve_fits" else "proportion"
            P, a, b = c_data['P'], c_data['a'], c_data['b']
            estimation = c_data['estimation']
            analysis_value = c_data['analysis_value']
            analysis_mode = c_data['analysis_mode']

            if utils.non_heatmap_methods(method) and type_of_curve != "power_curve_fits":
                return f"For method {method},\n the {metric} does not apply"

            fit_line = (f"Fit for {method}:"
                        f"\n {metric.capitalize()}(n) = {P:.3f}/(1+({a:.3f}/n)^{b:.3f})")

            if analysis_mode == "n_subjects":
                warning = f"\n Below minimum estimated N ({sub_list[0]})" if analysis_value < sub_list[0] else ""
                result_line = f"For {int(analysis_value)} subjects:\n Estimated {metric} = {estimation:.3f}{warning}"
            else:
                if estimation <= 0:
                    result_line = f"For desired {metric} of {analysis_value:.2f}:\n no solution (check parameters)"
                else:
                    warning = f"\n Below minimum estimated N ({sub_list[0]})" \
                    if estimation < sub_list[0] else ""
                    result_line = f"For desired {metric} of {analysis_value:.2f}:\n \
                    ~{int(estimation)} subjects required{warning}"

            return f"{result_line}\n{fit_line}"


    @reactive.effect
    def _register_outputs():
        for folder_name in matched_folders():
            register_card_outputs(folder_name)


app = App(app_ui, server, static_assets={"/static": BASE_DIR / "static"})

if __name__ == '__main__':

    pass

