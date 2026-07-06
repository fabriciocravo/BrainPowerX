  %% generate_plots.m
% Generates power curve plots, heatmaps, and CSV exports for BrainPowerX.
%
% Handles two file structures:
%
%   Old structure:
%     - Method names: Parametric_FWER, Parametric_FDR, Size, Fast_TFCE,
%                     Constrained_FWER, Constrained_FDR, Omnibus_Multidimensional_cNBS
%     - Power field:  positives / total_calculations * 100
%     - meta_data fields: data_set_base, data_set_map, test_name, test_type,
%                         n_subs_subset, mask, edge_groups
%
%   New structure:
%     - Method names: Size_cpp, Fast_TFCE_cpp, Constrained_cpp_FWER,
%                     Constrained_cpp_FDR, Omnibus_cNBS
%     - Power field:  tpr * 100
%     - meta_data fields: dataset, map, output, test_type, n_subs,
%                         mask, edge_groups
%
% Detection: isfield(meta_data, 'dataset') -> new, else -> old
%
% External functions required on path:
%   - extract_power.m
%   - fit_power_curve.m
%   - power_curve_fn.m
%   - unflatten_matrix.m
%
% Author: Fabricio Cravo
% Date:   March 2026

clear; clc;

fprintf('Started Generate Plot Scripts\n');

% ─────────────────────────────────────────────
%  CONFIG
% ─────────────────────────────────────────────

% comment and uncomment for desired one
data_folder = ["/Users/f.cravogomes/Desktop/Pc_Res_Updated/Shinny_Calculator/hcp_fc"]; % HCP
% data_folder = ["/Users/f.cravogomes/Desktop/Pc_Res_Updated/Shinny_Calculator/abcd_100_reps"]; % ABCD
% data_folder = ["/Users/f.cravogomes/Desktop/Pc_Res_Updated/Shinny_Calculator/hpc_activation"] % HCP
% data_folder = ["/Users/f.cravogomes/Desktop/Pc_Res_Updated/Shinny_Calculator/hbn_fc"] % HBN


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
addpath(genpath(fileparts(mfilename('fullpath'))));

% Todo
% Add to metadata.json - the power curves
% Fix images


% ─────────────────────────────────────────────
%  LOAD ALL FILES
% ─────────────────────────────────────────────
power_mat_files = dir(fullfile(data_folder, '*.mat'));
if isempty(power_mat_files)
    error('No .mat files found in %s', data_folder);
end
fprintf('Found %d .mat files.\n', length(power_mat_files));

% Replace this with a map if there are non complete studies
first_file = load(fullfile(power_mat_files(1).folder, power_mat_files(1).name));
ALL_METHODS = first_file.meta_data.method_list;

result_data_subs_grouped = extract_power_data( ...
  power_mat_files, ...
  ALL_METHODS ...
);

% Define quantilies to calculate top average power
QUANTILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1];


%%% Json index definition
%%% It's supposed to help searching the specific files
%%% Search terms contain the names of their respective folders
grouping_keys = fieldnames(result_data_subs_grouped);

for key_idx = 1:length(grouping_keys)
    grouping_key  = grouping_keys{key_idx};
    grouped_data = result_data_subs_grouped.(grouping_key);

    fprintf( ...
        '[%d/%d] Processing: %s\n', ...
        key_idx, ...
        length(grouping_keys), ...
        grouping_key ...
    );

    % Get the average power structure
    [power_by_method, sample_sizes] = get_average_power_struct( ...
        grouped_data, ...
        ALL_METHODS ...
    );

    % Pass sample_sizes in group data to reduce signature burden
    grouped_data.sample_sizes = sample_sizes;

    output_group_dir = create_output_directory( ...
        fullfile('results', grouping_key) ...
    );
    
    % Sample reason for the sample_sizes
    grouped_data.output_group_dir = output_group_dir;

    method_level = find_method_level( ...
        power_by_method, ...
        grouped_data.n_variables, ...
        grouped_data.edge_groups, ...
        ALL_METHODS ...
    );

    proportion_level = get_brain_variable_proportion( ...
        grouped_data.n_variables, ...
        grouped_data.edge_groups ...
    );
    
    % For each quantile - calculate power and draw figure
    % Each quantile percentage gets a power curve
    quantile_curve_fits = struct();
    for q_index = 1:numel(QUANTILES)
        quantile_percentage = QUANTILES(q_index); 

        quantile_average = get_quantile_average_power( ...
            quantile_percentage, ...
            power_by_method, ...
            sample_sizes, ...
            method_level, ...
            proportion_level, ...
            ALL_METHODS ...
        );
        
        % The curve fits
        curve_fits = get_power_curves( ...
            quantile_average, ...
            sample_sizes, ...
            ALL_METHODS ...
        );

        % Plot figure 
        mean_figure_generation( ...
            quantile_percentage, ...
            quantile_average, ...
            grouped_data, ...
            curve_fits, ...
            ALL_METHODS ...
        );

        % Get sample size key
        q_key = sprintf( ...
            'power_fit_q%d', ...
            round(QUANTILES(q_index) * 100) ...
        );
        quantile_curve_fits.(q_key) = curve_fits;
    end
    fprintf( ...
        '  [OK] All %s quantile power curves saved.\n', ...
        grouping_key ...
    );  

    % Heat map curve figure generation
    for n_idx = 1:length(sample_sizes)
        sample_size_index = n_idx;
        current_n         = sample_sizes(n_idx);

        % Heatmap generation here
        heatmap_figure_generation( ...
            sample_size_index, ...
            power_by_method, ...
            method_level, ...
            grouped_data, ...
            ALL_METHODS ...
        );

    end

    fprintf( ...
        '  [OK] All %s heatmap images saved.\n', ...
        grouping_key ...
    );  


    % Create json for saving raw data
    json_data_writer( ...
        quantile_curve_fits, ...
        grouped_data, ...
        ALL_METHODS ...
    );

end

fprintf('\nAll done!\n');
