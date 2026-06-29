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

% Put this somewhere
% ------ OUTPUT DIRECTORY DEFINITION
%output_group_dir = fullfile('results', grouping_key);
%if ~exist(output_group_dir, 'dir')
%    mkdir(output_group_dir)
%end

%%% Json index definition
%%% It's supposed to help searching the specific files
%%% Search terms contain the names of their respective folders
grouping_keys = fieldnames(result_data_subs_grouped);

for key_idx = 1:length(grouping_keys)
    grouping_key  = grouping_keys{key_idx};
    grouped_data = result_data_subs_grouped.(grouping_key);

    dataset     = grouped_data.dataset;
    map_type    = grouped_data.map_type;
    task        = grouped_data.task;
    test        = grouped_data.test;
    mask        = grouped_data.mask;
    edge_groups = grouped_data.edge_groups;
    n_variables = grouped_data.n_variables;

    % Get the average power structure

    power_by_method = get_average_power_struct( ...
        grouped_data, ...
        ALL_METHODS ...
    );

    keyboard;

    find_method_type(power_by_method, edge_groups, ALL_METHODS)
    
    keyboard;
    
    method_variable_propotion = get_brain_variable_proportion( ...
        power_by_method, ...
        edge_groups ...
    );
    
    keyboard;
      
end

fprintf('\nAll done!\n');
