import json
from math import ceil
from .map_files.file_to_outcome import FILE_TO_OUTCOME
from .map_files.method_to_display_name import METHOD_DISPLAY_NAMES
from .map_files.outcome_to_file import OUTCOME_TO_FILE
from .map_files.non_heatmap_method_names import NON_HEATMAP_METHODS
from .map_files.method_aliases import METHOD_NAME_TO_ALIAS

def compile_options(options_dict):

    DATASETS = options_dict["datasets"]
    MAP_TYPES = options_dict["maps"]
    OUTCOMES = options_dict["outcomes"]
    TEST_TYPES = options_dict["test_types"]
    SAMPLE_SIZES = options_dict["sample_sizes"]
    METHODS = options_dict["methods"]
    CURVE_CHOICE = options_dict["curve_choices"]

    return DATASETS, MAP_TYPES, OUTCOMES, TEST_TYPES, SAMPLE_SIZES, METHODS, CURVE_CHOICE


def get_index(json_path):

    with open(json_path) as jf:
        index_json = json.load(jf)

    return index_json


def method_display_name(method: str) -> str:
    if method not in METHOD_DISPLAY_NAMES:
        raise ValueError(f"Method not supported: {method}")
    return METHOD_DISPLAY_NAMES[method]


# This is here because shiny is not good
def safe_input(input, key):
    try:
        return input[key]()
    except Exception:
        raise KeyError(f"Input '{key}' not found — does the UI element exist?")


def outcome_map_names(outcome_menu_name: str) -> list:
    if outcome_menu_name not in OUTCOME_TO_FILE:
        raise ValueError(f"Outcome not supported: {outcome_menu_name}")
    return OUTCOME_TO_FILE[outcome_menu_name]


def reverse_outcome_map(outcome_file_name: str) -> str:
    if outcome_file_name not in FILE_TO_OUTCOME:
        raise ValueError(f"Outcome not supported: {outcome_file_name}")
    return FILE_TO_OUTCOME[outcome_file_name]


def non_heatmap_methods(method: str) -> bool:

    alias = METHOD_NAME_TO_ALIAS[method]

    if alias in NON_HEATMAP_METHODS:
        return True
    else:
        return False


def return_method_from_alias(alias_list, meta_data_method_list):

    for method_name in alias_list:
        if method_name in meta_data_method_list:
            return method_name
    else:
        raise ValueError("Method Not Found in Meta Data")

# This could be changed for an interpolation if more datapoints are added
def get_result_value_from_meta_data(
        metadata: dict,
        type_of_curve: str,
        method: iter,
    ) -> tuple:

    # Meta data is clearly a dictionary - not a hashable
    P = metadata[type_of_curve][method]["P"]
    a = metadata[type_of_curve][method]["a"]
    b = metadata[type_of_curve][method]["b"]

    return P, a, b


def get_subject_number_from_desired_power(R: float, P: float, a: float, b: float) -> int:

    base = P/R - 1
    if base < 0:
        return -1

    deno = (base)**(1/b)
    n = a/deno

    if n > 0:
        return ceil(n)
    else:
        return -1


def get_power_from_desired_subjects(n: float, P: float, a: float, b: float) -> int:

    deno = 1 + (a/n)**b
    return P/deno


def find_estimation_of_desired_value(
        user_value: float, 
        analysis_type: str, 
        P: float,
        a: float,
        b: float,
    ) -> float:

    if analysis_type == 'desired_power':
        estimation = get_subject_number_from_desired_power(user_value, P, a, b)
    elif analysis_type == 'n_subjects':
        estimation = get_power_from_desired_subjects(user_value, P, a, b)
    else:
        raise ValueError('Analysis type not supported')
    
    return estimation


def find_closest_n_sub_to_estimation():
    pass

