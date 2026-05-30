OUTCOME_TO_FILE = {
    # HCP tasks
    "Emotion":        {"REST_EMOTION", "EMOTION"},
    "Gambling":       {"REST_GAMBLING", "GAMBLING"},
    "Relational":     {"REST_RELATIONAL", "RELATIONAL"},
    "Social":         {"REST_SOCIAL", "SOCIAL", "social_responsiveness"},
    "Working Memory": {"REST_WM", "WM", "working_memory"},
    # ABCD demographics
    "Sex":         {"sex"},
    "WISC-V IQ":   {"wisc_v_iq"},
    "Age":         {"age"},
    "BMI z-score": {"bmi_z"},
    # ABCD CBCL baseline
    "CBCL Internalizing":    {"cbcl_internalizing"},
    "CBCL Externalizing":    {"cbcl_externalizing"},
    "CBCL Aggressive":       {"cbcl_aggressive"},
    "CBCL Rule Breaking":    {"cbcl_rule_breaking"},
    "CBCL Attention":        {"cbcl_attention"},
    "CBCL Thought Problems": {"cbcl_thought"},
    "CBCL Social Problems":  {"cbcl_social"},
    "CBCL Somatic":          {"cbcl_somatic"},
    "CBCL Withdrawn":        {"cbcl_withdrawn"},
    "CBCL Anxious/Depressed":{"cbcl_anx_dep"},
    # ABCD UPPS impulsivity
    "UPPS Lack of Planning":     {"upps_lack_planning"},
    "UPPS Lack of Perseverance": {"upps_lack_perseverance"},
    "UPPS Sensation Seeking":    {"upps_sensation_seeking"},
    "UPPS Negative Urgency":     {"upps_neg_urgency"},
    "UPPS Positive Urgency":     {"upps_pos_urgency"},
    # ABCD substance use
    "Substance Use": {"substance_use"},
    # ABCD CBCL follow-up 1
    "CBCL Internalizing (FU1)":    {"cbcl_internalizing_fu1"},
    "CBCL Externalizing (FU1)":    {"cbcl_externalizing_fu1"},
    "CBCL Aggressive (FU1)":       {"cbcl_aggressive_fu1"},
    "CBCL Rule Breaking (FU1)":    {"cbcl_rule_breaking_fu1"},
    "CBCL Attention (FU1)":        {"cbcl_attention_fu1"},
    "CBCL Thought Problems (FU1)": {"cbcl_thought_fu1"},
    "CBCL Social Problems (FU1)":  {"cbcl_social_fu1"},
    "CBCL Somatic (FU1)":          {"cbcl_somatic_fu1"},
    "CBCL Withdrawn (FU1)":        {"cbcl_withdrawn_fu1"},
    "CBCL Anxious/Depressed (FU1)":{"cbcl_anx_dep_fu1"},
    # ABCD CBCL change scores
    "CBCL Internalizing (Δ)":    {"cbcl_internalizing_delta"},
    "CBCL Externalizing (Δ)":    {"cbcl_externalizing_delta"},
    "CBCL Aggressive (Δ)":       {"cbcl_aggressive_delta"},
    "CBCL Rule Breaking (Δ)":    {"cbcl_rule_breaking_delta"},
    "CBCL Attention (Δ)":        {"cbcl_attention_delta"},
    "CBCL Thought Problems (Δ)": {"cbcl_thought_delta"},
    "CBCL Social Problems (Δ)":  {"cbcl_social_delta"},
    "CBCL Somatic (Δ)":          {"cbcl_somatic_delta"},
    "CBCL Withdrawn (Δ)":        {"cbcl_withdrawn_delta"},
    "CBCL Anxious/Depressed (Δ)":{"cbcl_anx_dep_delta"},
    # HBN cognitive (NIH Toolbox)
    "Cognitive Flexibility": {"cognitive_flexibility"},
    "Inhibitory Control":    {"inhibitory_control"},
    "Processing Speed":      {"processing_speed"},
}

FILE_TO_OUTCOME = {
    file: outcome
    for outcome, files in OUTCOME_TO_FILE.items()
    for file in files
}