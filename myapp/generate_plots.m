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

% ─────────────────────────────────────────────
%  CONFIG
% ─────────────────────────────────────────────
data_folder = "/Users/f.cravogomes/Desktop/Cloned Repos/PRISME-Brain-Power-Calculator/" + ...
    "power_calculator_results/previous_data_structure/power_calculation/hcp_fc";
output_root = fullfile(fileparts(mfilename('fullpath')), 'data', 'hcp_fc_tasks');

addpath(genpath(fileparts(mfilename('fullpath'))));


% ─────────────────────────────────────────────
%  LOAD ALL FILES
% ─────────────────────────────────────────────
power_mat_files = dir(fullfile(data_folder, '*.mat'));
if isempty(power_mat_files)
    error('No .mat files found in %s', data_folder);
end
fprintf('Found %d .mat files.\n', length(power_mat_files));

result_data_subs_grouped = struct();

% Replace this with a map if there are non complete studies
first_file = load(fullfile(power_mat_files(1).folder, power_mat_files(1).name));
ALL_METHODS = first_file.meta_data.method_list;

POWER_THRESHOLDS = [80, 50, 20];

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
        task        = meta_data.output;
        test        = meta_data.test_type;
        n_subs      = meta_data.n_subs;
        mask        = meta_data.mask;
        edge_groups = meta_data.edge_groups;
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
    end

    grouping_key = matlab.lang.makeValidName( ...
        sprintf('%s_%s_%s_%s', dataset, map_type, task, test));

    if ~isfield(result_data_subs_grouped, grouping_key) || ...
        ~isfield(result_data_subs_grouped.(grouping_key), 'mask')
        result_data_subs_grouped.(grouping_key).mask        = mask;
        result_data_subs_grouped.(grouping_key).edge_groups = edge_groups;
        result_data_subs_grouped.(grouping_key).dataset     = dataset;
        result_data_subs_grouped.(grouping_key).map_type    = map_type;
        result_data_subs_grouped.(grouping_key).task        = task;
        result_data_subs_grouped.(grouping_key).test        = test;
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


%%% Json index definition
%%% It's supposed to help searching the specific files 
%%% Search terms contain the names of their respective folders 
grouping_keys = fieldnames(result_data_subs_grouped);
fprintf('\nGrouped into %d combinations.\n\n', length(grouping_keys));

json_dir = fullfile('results', 'data_base_index.json');
if isfile(json_dir)
    json_index = json_to_struct(json_dir);
else
    json_index = struct();
end

for key_idx = 1:length(grouping_keys)
    grouping_key  = grouping_keys{key_idx};
    grouped_data = result_data_subs_grouped.(grouping_key);

    dataset     = grouped_data.dataset;
    map_type    = grouped_data.map_type;
    task        = grouped_data.task;
    test        = grouped_data.test;
    mask        = grouped_data.mask;
    edge_groups = grouped_data.edge_groups;

    % Collect sorted sample sizes from n* fields
    grouped_data_fields      = fieldnames(grouped_data);

    is_sample_size_field  = startsWith(grouped_data_fields, 'n') & ...
                            cellfun(@(x) ~isnan(str2double(x(2:end))), ...
                            grouped_data_fields);

    sample_sizes          = sort(cellfun(@(x) str2double(x(2:end)), ...
        grouped_data_fields(is_sample_size_field)));

    % ------ OUTPUT DIRECTORY DEFINITION
    output_group_dir = fullfile('results', grouping_key);
    if ~exist(output_group_dir, 'dir')
        mkdir(output_group_dir)
    end

    fprintf('Processing: %s_%s / %s / %s  [n = %s]\n', ...
        dataset, map_type, task, test, ...
        strjoin( ...
        arrayfun(@num2str, sample_sizes, 'UniformOutput', false), ', '));

    % ------ AVERAGE POWER CALCULATION AND FIGURES
    avg_power = struct();
    for method_idx = 1:length(ALL_METHODS)

        method = ALL_METHODS{method_idx};
        mean_power_by_n = nan(1, length(sample_sizes));

        for n_idx = 1:length(sample_sizes)

            sample_size_key = sprintf('n%d', sample_sizes(n_idx));
            mean_power_by_n(n_idx) = mean( ...
                grouped_data.(sample_size_key).(method), 'omitnan' ...
                );

        end
        avg_power.(method) = mean_power_by_n;
    end

    % Fiting power curves
    curve_fits = struct();
    for method_idx = 1:length(ALL_METHODS)

        method          = ALL_METHODS{method_idx};
        mean_power_by_n = avg_power.(method);

        if numel(mean_power_by_n) >= 3
            curve_fits.(method) = fit_power_curve(sample_sizes, mean_power_by_n);
        else
            error('A curve fit did not have enough values')
        end

    end

    % Average power figures
    fig = figure('Visible', 'off', 'Color', [0.06 0.07 0.10], ...
                 'Position', [0 0 900 500]);
    ax  = axes('Parent', fig, ...
               'Color',     [0.10 0.11 0.18], ...
               'XColor',    [0.58 0.64 0.73], ...
               'YColor',    [0.58 0.64 0.73], ...
               'GridColor', [0.16 0.19 0.29], ...
               'GridAlpha', 0.4);
    hold(ax, 'on');
    grid(ax, 'on');
    
    for method_idx = 1:length(ALL_METHODS)
        method          = ALL_METHODS{method_idx};
        mean_power_by_n = avg_power.(method);
        color           = color_method_map(method);
    
        scatter(ax, sample_sizes, mean_power_by_n, 60, ...
            color, 'filled', 'HandleVisibility', 'off');
    
        if ~isempty(curve_fits.(method))
            fitted_curve   = curve_fits.(method);
            n_interpolated = linspace(min(sample_sizes), ...
                max(sample_sizes) * 2, 300);
            fitted_power   = power_curve_fn(n_interpolated, ...
                fitted_curve.P, fitted_curve.a, fitted_curve.b);
            plot(ax, n_interpolated, fitted_power, ...
                'Color',       color, ...
                'LineWidth',   2, ...
                'DisplayName', sprintf('%s  (P=%.1f  a=%.1f  b=%.2f)', ...
                    method, fitted_curve.P, fitted_curve.a, fitted_curve.b));
        else
            plot(ax, nan, nan, 'Color', color, 'LineWidth', 2, ...
                'DisplayName', sprintf('%s  (insufficient data)', method));
        end
    end
    
    yline(ax, 80, '--', 'Color', [0.96 0.62 0.07], 'LineWidth', 1.2, 'Alpha', 0.7);
    legend(ax, 'TextColor', [0.89 0.91 0.94], ...
        'Color', [0.10 0.11 0.18], 'EdgeColor', [0.30 0.33 0.45], ...
        'Location', 'southeast');
    xlabel(ax, 'Sample size (n)', 'Color', [0.89 0.91 0.94]);
    ylabel(ax, 'Power (%)',       'Color', [0.89 0.91 0.94]);
    ylim(ax, [-2 105]);
    title(ax, sprintf('%s | %s | %s | test=%s', upper(dataset), upper(map_type), task, test), ...
        'Color', [0.89 0.91 0.94], 'FontSize', 12, 'FontWeight', 'bold');
    
    exportgraphics(fig, fullfile(output_group_dir, 'average_power_curves.png'), ...
        'Resolution', 150, 'BackgroundColor', [0.06 0.07 0.10]);
    close(fig);
    fprintf('  [OK] Power curves saved.\n');
    
    % ---- DETECTABLE PROPORTION OF VARIABLES -----------------------------
    % For each method with > 5 edges, plot proportion of edges above 20/50/80%
    % power across sample sizes. Total edge count shown in title.

    threshold_labels = arrayfun(@(t) sprintf('Above %d%%', t), ...
        POWER_THRESHOLDS, 'UniformOutput', false);

    % Determine which methods qualify (> 5 variabeles at any n)
    % Not edge methods - all methods - Honestly just pl
    qualifying_methods = {};
    for method_idx = 1:length(ALL_METHODS)
        method = ALL_METHODS{method_idx};

        for n_idx = 1:length(sample_sizes)
            sample_size_key = sprintf('n%d', sample_sizes(n_idx));

            power_vec = grouped_data.(sample_size_key).(method);
            
            % Cut methods with less then 5 variables
            if numel(power_vec) > 5
                qualifying_methods{end+1} = method; %#ok<SAGROW>
                break
            end

            
        end
    end
    
    if isempty(qualifying_methods)
        error('No qualifying methods - Stop execution')
    end


    % method_variable_counts(method_idx) — number of variables for each
    method_variable_counts  = nan(1, length(qualifying_methods));

    % proportions(method_idx, n_idx, threshold_idx)
    edge_proportions = nan( ...
        length(qualifying_methods), ...
        length(sample_sizes), ...
        length(POWER_THRESHOLDS) ...
        );

    for method_idx = 1:length(qualifying_methods)
    
        method = qualifying_methods{method_idx};
        for n_idx = 1:length(sample_sizes)
            sample_size_key = sprintf('n%d', sample_sizes(n_idx));
            
            power_values = grouped_data.(sample_size_key).(method);                 
            n_total = numel(power_values);
            method_variable_counts(method_idx) = n_total;
            
            for thr_idx = 1:length(POWER_THRESHOLDS)
                thr = POWER_THRESHOLDS(thr_idx);
                n_above = sum(power_values > thr);
                edge_proportions(method_idx, n_idx, thr_idx) = ...
                    n_above / n_total * 100;
            end
        end
    end

    % Fit power curves to proportion data: fits(method_idx, thr_idx)
    proportion_fits = cell( ...
        length(qualifying_methods), ...
        length(POWER_THRESHOLDS) ...
        );

    for method_idx = 1:length(qualifying_methods)

        for thr_idx = 1:length(POWER_THRESHOLDS)
            proportions = squeeze(edge_proportions(method_idx, :, thr_idx));
            
            if all(isnan(proportions))
                error('Method %d: array has no data', method_idx);
            end

            proportion_fits{method_idx, thr_idx} = fit_power_curve( ...
                sample_sizes, ...
                proportions ...
                );
        
        end

    end

    for thr_idx = 1:length(POWER_THRESHOLDS)

        fig = figure('Visible', 'off', 'Color', [0.06 0.07 0.10], ...
                     'Position', [0 0 900 380]);
        ax = axes(fig);
        set(ax, 'Color',     [0.10 0.11 0.18], ...
                'XColor',    [0.58 0.64 0.73], ...
                'YColor',    [0.58 0.64 0.73], ...
                'GridColor', [0.16 0.19 0.29], ...
                'GridAlpha', 0.4);
        hold(ax, 'on');
        grid(ax, 'on');
    
        for method_idx = 1:length(qualifying_methods)
            method      = qualifying_methods{method_idx};
            proportions = squeeze(edge_proportions(method_idx, :, thr_idx));
            c           = color_method_map(method);
    
            scatter(ax, sample_sizes, proportions, 40, c, 'filled', 'HandleVisibility', 'off');
    
            fitted = proportion_fits{method_idx, thr_idx};
            if ~isempty(fitted)
                n_dense      = linspace(min(sample_sizes), max(sample_sizes) * 2, 300);
                fitted_props = power_curve_fn(n_dense, fitted.P, fitted.a, fitted.b);
                legend_label = sprintf('%s  (N=%d)  P=%.1f a=%.1f b=%.2f', ...
                    method, method_variable_counts(method_idx), ...
                    fitted.P, fitted.a, fitted.b);
                plot(ax, n_dense, fitted_props, ...
                    'Color', c, 'LineWidth', 2, 'DisplayName', legend_label);
            else
                legend_label = sprintf('%s  (N=%d)  (insufficient data)', ...
                    method, method_variable_counts(method_idx));
                plot(ax, nan, nan, 'Color', c, 'LineWidth', 2, 'DisplayName', legend_label);
            end
        end
    
        legend(ax, 'TextColor', [0.89 0.91 0.94], ...
            'Color', [0.10 0.11 0.18], 'EdgeColor', [0.30 0.33 0.45]);
        title(ax, sprintf('%s | %s | %s | test=%s\n%s', ...
            upper(dataset), upper(map_type), task, test, threshold_labels{thr_idx}), ...
            'Color', [0.89 0.91 0.94], 'FontSize', 12, 'FontWeight', 'bold');
        xlabel(ax, 'Sample size (n)', 'Color', [0.89 0.91 0.94]);
        ylabel(ax, 'Edges above threshold (%)', 'Color', [0.89 0.91 0.94]);
        ylim(ax, [-2 105]);
    
        exportgraphics(fig, fullfile(output_group_dir, ...
            sprintf('edges_above_threshold_%d.png', POWER_THRESHOLDS(thr_idx))), ...
            'Resolution', 150, 'BackgroundColor', [0.06 0.07 0.10]);
        close(fig);
    end
    fprintf('  [OK] Edges above threshold figures saved.\n');

    % ── 4. HEATMAPS ───────────────────────────────────────────────────────
    for n_idx = 1:length(sample_sizes)
        current_n       = sample_sizes(n_idx);
        sample_size_key = sprintf('n%d', current_n);

        for method_idx = 1:length(ALL_METHODS)
            method    = ALL_METHODS{method_idx};
            power_vec = grouped_data.(sample_size_key).(method);
            n_edges   = sum(grouped_data.mask(:));
    
            if numel(power_vec) == n_edges
                % Edge case — direct unflatten
                power_matrix = unflatten_matrix(power_vec, grouped_data.mask);
    
            elseif max(grouped_data.edge_groups(:)) == numel(power_vec)
                % Network case — project network values into edge space, then unflatten
                power_matrix = unflatten_network( ...
                    power_vec, ...
                    grouped_data.edge_groups ...
                    );

            else
                fprintf('  [SKIP] %s: %d variables — cannot map to edge or network space.\n', ...
                    method, numel(power_vec));
                continue
            end
    
            fig = figure('Visible', 'off', 'Color', [0.06 0.07 0.10], ...
                         'Position', [0 0 800 700]);
            ax  = axes('Parent', fig, ...
                       'Color',  [0.10 0.11 0.18], ...
                       'XColor', [0.58 0.64 0.73], ...
                       'YColor', [0.58 0.64 0.73]);
    
            imagesc(ax, power_matrix, [0 100]);
            colormap(ax, hot);
            colorbar_handle              = colorbar(ax);
            colorbar_handle.Label.String = 'Power (%)';
            colorbar_handle.Color        = [0.89 0.91 0.94];
    
            title(ax, sprintf('%s | %s | %s | test=%s\n%s  |  n=%d', ...
                upper(dataset), upper(map_type), task, test, method, current_n), ...
                'Color', [0.89 0.91 0.94], 'FontSize', 10);
            xlabel(ax, 'Node index', 'Color', [0.89 0.91 0.94]);
            ylabel(ax, 'Node index', 'Color', [0.89 0.91 0.94]);
            axis(ax, 'square');
    
            exportgraphics(fig, fullfile(output_group_dir, sprintf('heatmap_%s_%s.png', method, ...
                sample_size_key)), ...
                'Resolution', 150, 'BackgroundColor', [0.06 0.07 0.10]);
            close(fig);
        end

    end
    

    fprintf('  [OK] Heatmaps saved for n = [%s].\n', ...
    strjoin(arrayfun(@num2str, sample_sizes, 'UniformOutput', false), ', '));

    % ── EXPORT grouped_data as json ────────────────────────────
    fid = fopen(fullfile(output_group_dir, 'power_data.json'), 'w');
    fprintf(fid, '%s', jsonencode(grouped_data, 'PrettyPrint', true));
    fclose(fid);
    fprintf('  [OK] Power data JSON saved.\n');
    
    fields = {dataset, map_type, task, test};
    for i = 1:length(fields)
        key = matlab.lang.makeValidName(fields{i});
        if ~isfield(json_index, key)
            json_index.(key) = {};
        end
        json_index.(key){end+1} = output_group_dir;
    end

    fid = fopen(json_dir, 'w');
    fprintf(fid, '%s', jsonencode(json_index, 'PrettyPrint', true));
    fclose(fid);

end 

fprintf('\nAll done! Outputs under: %s\n', output_root);