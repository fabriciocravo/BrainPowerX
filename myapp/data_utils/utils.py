import json
from math import ceil


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
    if method == "Parametric_FWER":
        return "Par. FWER"
    elif method == "Parametric_FDR":
        return "Par. FDR"
    elif method == "Size":
        return "Size"
    elif method == "Fast_TFCE":
        return "TFCE"
    elif method == "Constrained_FWER":
        return "cNBS FWER"
    elif method == "Constrained_FDR":
        return "cNBS FDR"
    else:
        return method



def outcome_display_name(experiment:str) -> str:
    pass


# This is here because shiny is not good
def safe_input(input, key):
    try:
        return input[key]()
    except Exception:
        raise KeyError(f"Input '{key}' not found — does the UI element exist?")


def outcome_map_names(outcome_menu_name:str) -> list:
    outcome_menu_name = outcome_menu_name.strip()

    if outcome_menu_name == 'EMOTION':
        return ["REST_EMOTION"]
    elif outcome_menu_name == 'GAMBLING':
        print('Yeah')
        return ["REST_GAMBLING"]
    elif outcome_menu_name == "RELATIONAL":
        return ["REST_RELATIONAL"]
    elif outcome_menu_name == "SOCIAL":
        return ["REST_SOCIAL"]
    elif outcome_menu_name == "WORKING MEMORY":
        return ["REST_WM"]
    else:
        return []


def reverse_outcome_map(outcome_file_name: str) -> str:
    outcome_file_name = outcome_file_name.strip()

    if outcome_file_name == 'REST_EMOTION':
        return "EMOTION"
    elif outcome_file_name == 'REST_GAMBLING':
        return "GAMBLING"
    elif outcome_file_name == "REST_RELATIONAL":
        return "RELATIONAL"
    elif outcome_file_name == "REST_SOCIAL":
        return "SOCIAL"
    elif outcome_file_name == "REST_WM":
        return "WORKING MEMORY"
    else:
        raise TypeError(f"Outcome {outcome_file_name} is not mapped to an outcome name")


# This could be changed for an interpolation if more datapoints are added
def get_result_value_from_meta_data(
        metadata: dict,
        type_of_curve: str,
        method: str,
    ) -> tuple:

    #print("type of curve")
    #print(type_of_curve)
    #print("method")
    #print(method)

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
