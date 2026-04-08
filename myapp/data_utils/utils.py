import json



def compile_options(json_path):

    with open(json_path) as jf:
        options_json = json.load(jf)

    DATASETS = options_json["datasets"]
    MAP_TYPES = options_json["maps"]
    TASKS = options_json["tasks"]

    return DATASETS, MAP_TYPES, TASKS


def get_index(json_path):

    with open(json_path) as jf:
        index_json = json.load(jf)

    return index_json



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


