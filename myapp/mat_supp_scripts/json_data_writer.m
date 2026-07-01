function json_data_writer( ...
        quantile_curve_fits, ...
        grouped_data, ...
        ALL_METHODS ...
)
     
    % Create json and save
    metadata_json = struct();
    metadata_json.sample_sizes = grouped_data.sample_sizes;
    metadata_json.method_list = ALL_METHODS;
    metadata_json.dataset = grouped_data.dataset;
    metadata_json.map = grouped_data.map_type;
    metadata_json.outcome = grouped_data.task;
    metadata_json.test_type = grouped_data.test;

    % One curve-fit block per quantile, whatever keys the driver used
    q_keys = fieldnames(quantile_curve_fits);
    for q_idx = 1:numel(q_keys)
        q_key = q_keys{q_idx};
        metadata_json.(q_key) = quantile_curve_fits.(q_key);
    end
    
    fid = fopen( ...
        fullfile(grouped_data.output_group_dir, 'metadata.json'), ...
        'w' ...
    );
    fprintf(fid, '%s', jsonencode(metadata_json));
    fclose(fid);
    fprintf('  [OK] Metadata JSON saved.\n');

end