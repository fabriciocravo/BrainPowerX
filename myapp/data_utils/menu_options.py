
OPTIONS = {

  "datasets": [
    "HCP",
    "UKB",
    "ABCD"
  ],

  "maps": [
    "FC",
    "ACT"
  ],

  "outcomes": [
    "EMOTION",
    "GAMBLING",
    "RELATIONAL",
    "SOCIAL",
    "WORKING MEMORY"
  ],

  "test_types":[
    "t",
    "t2",
    "r"
  ],

  "sample_sizes": [
    20, 40, 80, 120, 180, 200
  ],

  "methods":[
    "Parametric_FDR",
    "Parametric_FWER",
    "Size",
    "Fast_TFCE",
    "Constrained_FWER",
    "Constrained_FDR",
    "Omnibus_Multidimensional_cNBS"
  ],

  # Important - Please remind the app choice is based around having 20, 50, 80 in here
  # There are no conflicting cases, but in future expansions be careful when changing this
  "curve_choices":[
    "Average",
    "Proportion of variables  > 20",
    "Proportion of variables  > 50",
    "Proportion of variables  > 80"
  ]

}