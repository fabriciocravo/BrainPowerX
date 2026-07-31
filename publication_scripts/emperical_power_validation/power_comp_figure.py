
# Variable to set quantily percentage
# Either 10, 30, 50 or 100

# Power directory ./power_data/

# Glob all files from directory 

# Open gt_power.json - gt_json

# Define function receives meta-data returns study key

    # Key pattern
    # meta_data.output-meta_data.study_name-meta_data.test_type


# Create empty power dicionary

# For each file in power data

    # Retrieve key name from meta_data

    # Get subject number from meta_data.n_subs

    # Assign to set of possible subs

    # Get power data vector from Parametric_FWER.tpr

    # Calculate average power according to selected quantile 

    # Power dict: Store results in key name (y) and sub number (n)


# For each key in gt_json 

    # Remove -Ground_Truth from ending 
    # ex: hpc_fc_gt-REST_EMOTION-t-Ground_Truth

    # Create two lists - gt and subsampled

    # For each element in the set of possible subs

        # Get power value
        # gt_json[key]['n'+subnume]['q'+quantile]

        # Get respective result from power dict

    # plot curve 

    # Legend = task name 

    # Color - ligh version for gt, dark for est

# Show plot, not save



