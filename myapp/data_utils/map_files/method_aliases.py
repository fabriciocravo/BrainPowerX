METHOD_ALIASES = {
    "Parametric FDR":  {"Parametric_FDR"},
    "Parametric FWER": {"Parametric_FWER"},
    "Size":            {"Size", "Size_cpp", "Size_Node_cpp"},
    "TFCE":            {"Fast_TFCE", "Fast_TFCE_cpp", "IC_TFCE_Node_cpp"},
    "cNBS FWER":       {"Constrained_FWER", "Constrained_cpp_FWER"},
    "cNBS FDR":        {"Constrained_FDR", "Constrained_cpp_FDR"},
    "Omnibus cNBS":    {"Omnibus_Multidimensional_cNBS", "Omnibus_cNBS"},
}

METHOD_NAME_TO_ALIAS = {
    alias: ui_name
    for ui_name, aliases in METHOD_ALIASES.items()
    for alias in aliases
}