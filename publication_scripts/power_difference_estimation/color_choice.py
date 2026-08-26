
# Define function that removed GT name from file 
# Returns string name without gt

# Define function that removed GT name from file
# Returns string name without gt
def remove_gt_mat(name):
    name = name.replace(".mat", "")
    name = name.replace("-Ground_Truth", "")
    return name


# Define dictionary ex: file name hcp_fc_*_t to color
COLOR_DICT = {
    "hcp_fc_REST_EMOTION_t":"#4C72B0",
    "hcp_fc_REST_GAMBLING_t": "#DD8452",
    "hcp_fc_REST_RELATIONAL_t": "#55A868",
    "hcp_fc_REST_SOCIAL_t": "#C44E52",
    "hcp_fc_REST_WM_t": "#8172B3",
}

# Define dictionary ex: file name hcp_fc_*_t to task
TASK_DICT = {
    "hcp_fc_REST_EMOTION_t": "Emotion",
    "hcp_fc_REST_GAMBLING_t": "Gambling",
    "hcp_fc_REST_RELATIONAL_t": "Relational",
    "hcp_fc_REST_SOCIAL_t": "Social",
    "hcp_fc_REST_WM_t": "Working memory",
}
