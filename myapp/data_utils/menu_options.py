from .map_files.outcome_to_file import OUTCOME_TO_FILE


OPTIONS = {

  "datasets": [
    "HCP",
    "UKB",
    "ABCD",
    "HBN"
  ],

  "maps": [
    "FC",
    "ACT"
  ],

  "outcomes": list(OUTCOME_TO_FILE.keys()),

  "test_types": [
    "t",
    "t2",
    "r"
  ],

  "sample_sizes": [
    20, 40, 80, 120, 180, 200
  ],

  "methods": [
    "Parametric FDR",
    "Parametric FWER",
    "Size",
    "TFCE",
    "cNBS FWER",
    "cNBS FDR",
    "Omnibus cNBS"
  ],

  # Important - Please remind the app choice is based around having 20, 50, 80
  # in here
  # There are no conflicting cases, but in future expansions be careful when
  # changing this
  "quantiles": [
    "10%",
    "20%",
    "30%",
    "40%",
    "50%",
    "75%",
    "100%"
  ]

}
