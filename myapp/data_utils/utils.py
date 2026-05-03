import json


def compile_options(options_dict):

    DATASETS = options_dict["datasets"]
    MAP_TYPES = options_dict["maps"]
    TASKS = options_dict["tasks"]
    SAMPLE_SIZES = options_dict["sample_sizes"]
    METHODS = options_dict["methods"]
    CURVE_CHOICE = options_dict["curve_choices"]

    return DATASETS, MAP_TYPES, TASKS,  SAMPLE_SIZES, METHODS, CURVE_CHOICE


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


def task_map_names(task_menu_name:str) -> list:
    task_menu_name = task_menu_name.strip()

    if task_menu_name == 'EMOTION':
        return ["REST_EMOTION"]
    elif task_menu_name == 'GAMBLING':
        print('Yeah')
        return ["REST_GAMBLING"]
    elif task_menu_name == "RELATIONAL":
        return ["REST_RELATIONAL"]
    elif task_menu_name == "SOCIAL":
        return ["REST_SOCIAL"]
    elif task_menu_name == "WORKING MEMORY":
        return ["REST_WM"]
    else:
        return []