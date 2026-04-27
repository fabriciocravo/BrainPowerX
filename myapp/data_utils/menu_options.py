
OPTIONS = {

  "datasets": [
    "HPC",
    "UKB",
    "ABCD"
  ],

  "maps": [
    "FC",
    "ACT"
  ],

  "tasks": [
    "A",
    "B"
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
    "Constrained_FDR"
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