
# Define function that removed GT name from file 
# Returns string name without gt

# Define function that removed GT name from file
# Returns string name without gt
def remove_gt_mat(name):
    name = name.replace(".mat", "")
    name = name.replace("_gt", "")
    name = name.replace("-Ground_Truth", "")
    name = name.replace("-", "_")
    return name


COLOR_DICT = {
    "hcp_fc_REST_EMOTION_t": "#4C72B0",
    "hcp_fc_REST_GAMBLING_t": "#DD8452",
    "hcp_fc_REST_RELATIONAL_t": "#55A868",
    "hcp_fc_REST_SOCIAL_t": "#C44E52",
    "hcp_fc_REST_WM_t": "#8172B3",
    "hcp_act_EMOTION_t": "#4C72B0",
    "hcp_act_GAMBLING_t": "#DD8452",
    "hcp_act_RELATIONAL_t": "#55A868",
    "hcp_act_SOCIAL_t": "#C44E52",
    "hcp_act_WM_t": "#8172B3",
    # Physical studies (ABCD)
    "abcd_fc_sex_t2": "#4C72B0",
    "abcd_fc_age_r": "#DD8452",
    "abcd_fc_bmi_z_r": "#55A868",
    # CBCL syndrome scales (ABCD)
    "abcd_fc_cbcl_internalizing_r": "#4C72B0",
    "abcd_fc_cbcl_externalizing_r": "#DD8452",
    "abcd_fc_cbcl_aggressive_r": "#C44E52",
    "abcd_fc_cbcl_rule_breaking_r": "#8172B3",
    "abcd_fc_cbcl_attention_r": "#937860",
    "abcd_fc_cbcl_thought_r": "#DA8BC3",
    "abcd_fc_cbcl_social_r": "#8C8C8C",
    "abcd_fc_cbcl_somatic_r": "#CCB974",
    "abcd_fc_cbcl_withdrawn_r": "#64B5CD",
    "abcd_fc_cbcl_anx_dep_r": "#1F77B4",
}

TASK_DICT = {
    "hcp_fc_REST_EMOTION_t": "Emotion",
    "hcp_fc_REST_GAMBLING_t": "Gambling",
    "hcp_fc_REST_RELATIONAL_t": "Relational",
    "hcp_fc_REST_SOCIAL_t": "Social",
    "hcp_fc_REST_WM_t": "Working memory",
    "hcp_act_EMOTION_t": "Emotion",
    "hcp_act_GAMBLING_t": "Gambling",
    "hcp_act_RELATIONAL_t": "Relational",
    "hcp_act_SOCIAL_t": "Social",
    "hcp_act_WM_t": "Working memory",
    # Physical studies (ABCD)
    "abcd_fc_sex_t2": "Sex",
    "abcd_fc_age_r": "Age",
    "abcd_fc_bmi_z_r": "BMI",
    # CBCL syndrome scales (ABCD)
    "abcd_fc_cbcl_internalizing_r": "Internalizing problems",
    "abcd_fc_cbcl_externalizing_r": "Externalizing problems",
    "abcd_fc_cbcl_aggressive_r": "Aggressive behavior",
    "abcd_fc_cbcl_rule_breaking_r": "Rule-breaking behavior",
    "abcd_fc_cbcl_attention_r": "Attention problems",
    "abcd_fc_cbcl_thought_r": "Thought problems",
    "abcd_fc_cbcl_social_r": "Social problems",
    "abcd_fc_cbcl_somatic_r": "Somatic complaints",
    "abcd_fc_cbcl_withdrawn_r": "Withdrawn/depressed",
    "abcd_fc_cbcl_anx_dep_r": "Anxious/depressed",
}

