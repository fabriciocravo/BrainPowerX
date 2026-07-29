function result_data_subs_grouped = extract_power_data( ...
  power_mat_files, ...
  ALL_METHODS ...
)

  result_data_subs_grouped = struct();

  for file_idx = 1:length(power_mat_files)
    file_path = fullfile(power_mat_files(file_idx).folder, ...
        power_mat_files(file_idx).name);
    file_data = load(file_path);
    meta_data = file_data.meta_data;

    % ── Meta-data version detection ───────────────────────────────────────
    if ~isfield(meta_data, 'rep_parameters')
        % New structure
        dataset     = meta_data.dataset;
        map_type    = meta_data.map;
        task        = meta_data.study_name;
        test        = meta_data.test_type;
        n_subs      = meta_data.n_subs;
        mask        = meta_data.mask;
        edge_groups = meta_data.edge_groups;
        n_variables = sum(mask(:)); % I removed the variables here ....
        n_reps      = meta_data.n_repetitions;
    else
        % Old structure
        dataset     = meta_data.dataset;
        map_type    = meta_data.map;
        task        = strcat(meta_data.test_components{1},'_', ...
            meta_data.test_components{2});
        test        = meta_data.test;
        n_subs      = meta_data.subject_number;
        mask        = meta_data.rep_parameters.mask;
        edge_groups = meta_data.rep_parameters.edge_groups;
        n_variables = meta_data.rep_parameters.n_var;
        n_reps      = meta_data.rep_parameters.n_repetitions;
    end

    % Skip some outcomes that did not have enough subjects - etc
    if skip_outcome(dataset, task)
      continue
    end

    % Map task to name of outcome
    task = map_task_to_outcome( ...
        dataset, ...
        task ...
    );

    grouping_key = make_valid_name( ...
      sprintf('%s_%s_%s_%s', dataset, map_type, task, test) ...
    );

    if ~isfield(result_data_subs_grouped, grouping_key) || ...
        ~isfield(result_data_subs_grouped.(grouping_key), 'mask')
        result_data_subs_grouped.(grouping_key).mask        = mask;
        result_data_subs_grouped.(grouping_key).edge_groups = edge_groups;
        result_data_subs_grouped.(grouping_key).dataset     = dataset;
        result_data_subs_grouped.(grouping_key).map_type    = map_type;
        result_data_subs_grouped.(grouping_key).task        = task;
        result_data_subs_grouped.(grouping_key).test        = test;
        result_data_subs_grouped.(grouping_key).n_variables = n_variables;
        result_data_subs_grouped.(grouping_key).n_reps      = n_reps;
    end

    % ── Extract power for each method ─────────────────────────────────────

    sample_size_key = sprintf('n%d', n_subs);
    for method_idx = 1:length(ALL_METHODS)
        method = ALL_METHODS{method_idx};
        if isfield(file_data, method)
            result_data_subs_grouped.(grouping_key).(sample_size_key).(method) ...
                = extract_power(file_data.(method));
        end
    end

    fprintf('  Loaded: %s\n', power_mat_files(file_idx).name);
  end

end
