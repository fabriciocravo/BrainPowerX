"""
   This script updates the database index.
   To construct the index structure used to retrieve the correct files queried by the user
"""
from pathlib import Path
import json

data_base_index = {}

BASE_DIR = Path(__file__).parent
results_dir = BASE_DIR / "results"

# Loop over everything
for d in Path(results_dir).iterdir():

    if not d.is_dir():
        continue

    metadata_path = d / 'metadata.json'
    directory_name = d.name

    with open(metadata_path, "r") as j:
        metadata = json.load(j)

    for key in {'dataset', 'map', 'outcome', 'test_type'}:

        if key == 'dataset' or key == 'map':
            index_key = metadata[key].upper()
        else:
            index_key = metadata[key]

        try:
            data_base_index[index_key] |= {directory_name}
        except KeyError:
            data_base_index[index_key] = {directory_name}

for key in data_base_index:
    data_base_index[key] = list(data_base_index[key])

with open(Path(results_dir) / "data_base_index.json", "w") as f:
    json.dump(data_base_index, f, indent=4)
