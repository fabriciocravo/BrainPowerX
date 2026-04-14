import json



def compile_options(options_dict):

    DATASETS = options_dict["datasets"]
    MAP_TYPES = options_dict["maps"]
    TASKS = options_dict["tasks"]
    SAMPLE_SIZES = options_dict["sample_sizes"]
    METHODS = options_dict["methods"]

    return DATASETS, MAP_TYPES, TASKS,  SAMPLE_SIZES, METHODS


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



"""
def _all_folders():
    folders = set()
    for v in INDEX.values():
        folders.update(v)
    return folders

def _parse_folders():
    datasets, map_types, tasks = set(), set(), set()
    for folder in _all_folders():
        name = folder.rstrip("/").split("/")[-1]   # strip path prefix
        parts = name.split("_")
        # For now:
        # parts[0]          → dataset   (hcp)
        # parts[1]          → map_type  (fc)
        # parts[2:-1]       → task      (REST, EMOTION → REST_EMOTION)
        # parts[-1]         → test_type (t)
        datasets.add(parts[0])
        map_types.add(parts[1])
        tasks.add("_".join(parts[2:-1]))
    return sorted(datasets), sorted(map_types), sorted(tasks)

# DATASETS, MAP_TYPES, TASKS = _parse_folders()
"""


