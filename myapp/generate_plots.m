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
data_folder = "C:\Users\Fabricio\Desktop\Cloned Repos\BrainPowerX\myapp\data\hpc_fc_tasks\power_calculation";
output_root = fullfile(fileparts(mfilename('fullpath')), 'data', 'hcp_fc_tasks');

addpath(genpath(fileparts(mfilename('fullpath'))));

% Old dataset method names
EDGE_METHODS    = {'Parametric_FWER', 'Parametric_FDR', 'Size', 'Fast_TFCE'};
NETWORK_METHODS = {'Constrained_FWER', 'Constrained_FDR'};
OMNIBUS_METHODS = {'Omnibus_Multidimensional_cNBS'};
ALL_METHODS     = [EDGE_METHODS, NETWORK_METHODS, OMNIBUS_METHODS];

POWER_THRESHOLDS = [80, 50, 20];

% ─────────────────────────────────────────────
%  LOAD ALL FILES
% ─────────────────────────────────────────────
power_mat_files = dir(fullfile(data_folder, '*.mat'));
if isempty(power_mat_files)
    error('No .mat files found in %s', data_folder);
end
fprintf('Found %d .mat files.\n', length(power_mat_files));

grouped_by_condition = struct();

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

    condition_key = matlab.lang.makeValidName( ...
        sprintf('%s_%s_%s_%s', dataset, map_type, task, test));

    if ~isfield(grouped_by_condition, condition_key) || ...
        ~isfield(grouped_by_condition.(condition_key), 'mask')
        grouped_by_condition.(condition_key).mask        = mask;
        grouped_by_condition.(condition_key).edge_groups = edge_groups;
        grouped_by_condition.(condition_key).dataset     = dataset;
        grouped_by_condition.(condition_key).map_type    = map_type;
        grouped_by_condition.(condition_key).task        = task;
        grouped_by_condition.(condition_key).test        = test;
    end

    % ── Extract power for each method ─────────────────────────────────────
    sample_size_key = sprintf('n%d', n_subs);
    for method_idx = 1:length(ALL_METHODS)
        method = ALL_METHODS{method_idx};
        if isfield(file_data, method)
            grouped_by_condition.(condition_key).(sample_size_key).(method) ...
                = extract_power(file_data.(method));
        end
    end

    fprintf('  Loaded: %s\n', power_mat_files(file_idx).name);
end

condition_keys = fieldnames(grouped_by_condition);
fprintf('\nGrouped into %d combinations.\n\n', length(condition_keys));

json_dir = fullfile('results', 'data_base_index.json');
if isfile(json_dir)
    json_index = json_to_struct(json_dir);
else
    json_index = struct();
end

for key_idx = 1:length(condition_keys)
    condition_key  = condition_keys{key_idx};
    condition_data = grouped_by_condition.(condition_key);

    dataset     = condition_data.dataset;
    map_type    = condition_data.map_type;
    task        = condition_data.task;
    test        = condition_data.test;
    mask        = condition_data.mask;
    edge_groups = condition_data.edge_groups;

    % Collect sorted sample sizes from n* fields
    condition_fields      = fieldnames(condition_data);

    is_sample_size_field  = startsWith(condition_fields, 'n') & ...
                            cellfun(@(x) ~isnan(str2double(x(2:end))), ...
                            condition_fields);

    sample_sizes          = sort(cellfun(@(x) str2double(x(2:end)), ...
        condition_fields(is_sample_size_field)));

    % This is wrong
    output_group_dir = fullfile('results', key);

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
            if isfield(condition_data, sample_size_key) && ....
                isfield(condition_data.(sample_size_key), method)

                mean_power_by_n(n_idx) = mean( ...
                    condition_data.(sample_size_key).(method), 'omitnan' ...
                    );
            end

        end
        avg_power.(method) = mean_power_by_n;
    end

    % Fiting power curves
    curve_fits = struct();
    for method_idx = 1:length(ALL_METHODS)

        method          = ALL_METHODS{method_idx};
        mean_power_by_n = avg_power.(method);
        has_data        = ~isnan(mean_power_by_n);

        if sum(has_data) >= 3
            curve_fits.(method) = fit_power_curve(sample_sizes(has_data), ...
                mean_power_by_n(has_data));
        else
            curve_fits.(method) = [];
        end

    end

    % Average power figures
    n_methods = length(ALL_METHODS);
    fig = figure('Visible', 'off', 'Color', [0.06 0.07 0.10], ...
                 'Position', [0 0 900 380*n_methods]);

    for method_idx = 1:n_methods
        method          = ALL_METHODS{method_idx};
        mean_power_by_n = avg_power.(method);
        has_data        = ~isnan(mean_power_by_n);

        ax = subplot(n_methods, 1, method_idx);
        set(ax, 'Color',     [0.10 0.11 0.18], ...
                'XColor',    [0.58 0.64 0.73], ...
                'YColor',    [0.58 0.64 0.73], ...
                'GridColor', [0.16 0.19 0.29], ...
                'GridAlpha', 0.4);
        hold(ax, 'on');
        grid(ax, 'on');

        scatter(ax, sample_sizes(has_data), mean_power_by_n(has_data), 60, ...
            [0.65 0.71 0.99], 'filled');

        if ~isempty(curve_fits.(method))

            fitted_curve   = curve_fits.(method);
            n_interpolated = linspace(min(sample_sizes(has_data)), ...
                max(sample_sizes(has_data)) * 2, 300);

            fitted_power   = power_curve_fn( ...
                n_interpolated, ...
                fitted_curve.P, ...
                fitted_curve.a, ...
                fitted_curve.b ...
                );

            plot( ...
                ax, ...
                n_interpolated, ...
                fitted_power, ...
                'Color', ...
                [0.02 0.71 0.84], ...
                'LineWidth', ...
                2 ...
                );

            plot_title = sprintf('%s  |  Fit: P=%.1f  a=%.1f  b=%.2f', ...
                method, fitted_curve.P, fitted_curve.a, fitted_curve.b);

        else
            
            plot_title = sprintf('%s  (insufficient data for fit)', method);

        end

        title(ax, plot_title, 'Color', [0.89 0.91 0.94], 'FontSize', 10);
        yline(ax, 80, '--', 'Color', [0.96 0.62 0.07], ...
            'LineWidth', 1.2, 'Alpha', 0.7);
        xlabel(ax, 'Sample size (n)', 'Color', [0.89 0.91 0.94]);
        ylabel(ax, 'Power (%)',       'Color', [0.89 0.91 0.94]);
        ylim(ax, [-2 105]);

    end

    output_group_dir = fullfile('results', key);
    if ~exist(output_group_dir, 'dir')
        mkdir(output_group_dir);
    end
    
    sgtitle(sprintf('%s | %s | %s | test=%s\nAverage Power Curves', ...
        upper(dataset), upper(map_type), task, test), ...
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
    qualifying_methods = {};
    for method_idx = 1:length(EDGE_METHODS)
        method = EDGE_METHODS{method_idx};

        for n_idx = 1:length(sample_sizes)
            sample_size_key = sprintf('n%d', sample_sizes(n_idx));
            if isfield(condition_data, sample_size_key) && ...
               isfield(condition_data.(sample_size_key), method)

                power_vec = condition_data.(sample_size_key).(method);
                
                % Cut methods with less then 5 variables
                if numel(power_vec) > 5
                    qualifying_methods{end+1} = method; %#ok<SAGROW>
                    break
                end

            end
        end
    end

    if ~isempty(qualifying_methods)

        % method_variable_counts(method_idx) — number of variables for each
        % method
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

                if ~isfield(condition_data, sample_size_key) || ...
                   ~isfield(condition_data.(sample_size_key), method)
                    continue
                end
                
                power_values = condition_data.(sample_size_key).(method);       
    
                if isnan(method_variable_counts(method_idx))
                    method_variable_counts(method_idx) = n_total;
                end
    
                for thr_idx = 1:length(POWER_THRESHOLDS)
                    thr = POWER_THRESHOLDS(thr_idx);
                    n_above = sum(power_matrix(:) > thr) / 2;
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
                has_data    = ~isnan(proportions);
                if sum(has_data) >= 3
                    proportion_fits{method_idx, thr_idx} = fit_power_curve( ...
                        sample_sizes(has_data), ...
                        proportions(has_data) ...
                        );
                else
                    proportion_fits{method_idx, thr_idx} = [];
                end
            end

        end

    method_colors = lines(length(qualifying_methods));

    fig = figure('Visible', 'off', 'Color', [0.06 0.07 0.10], ...
                 'Position', [0 0 900 380*length(POWER_THRESHOLDS)]);

    for thr_idx = 1:length(POWER_THRESHOLDS)
        ax = subplot(length(POWER_THRESHOLDS), 1, thr_idx);
        set(ax, 'Color',     [0.10 0.11 0.18], ...
                'XColor',    [0.58 0.64 0.73], ...
                'YColor',    [0.58 0.64 0.73], ...
                'GridColor', [0.16 0.19 0.29], ...
                'GridAlpha', 0.4);
        hold(ax, 'on');
        grid(ax, 'on');

        for method_idx = 1:length(qualifying_methods)
            proportions = squeeze(edge_proportions(method_idx, :, thr_idx));
            has_data    = ~isnan(proportions);
            c           = method_colors(method_idx, :);

            % Scatter raw points
            scatter(ax, sample_sizes(has_data), proportions(has_data), ...
                40, c, 'filled', 'HandleVisibility', 'off');

            % Fitted curve
            fitted = proportion_fits{method_idx, thr_idx};
            if ~isempty(fitted)
                n_dense      = linspace(min(sample_sizes(has_data)), ...
                    max(sample_sizes(has_data)) * 2, 300);
                fitted_props = power_curve_fn(n_dense, fitted.P, fitted.a, fitted.b);
                legend_label = sprintf('%s  (N=%d)  P=%.1f a=%.1f b=%.2f', ...
                    qualifying_methods{method_idx}, method_variable_counts(method_idx), ...
                    fitted.P, fitted.a, fitted.b);
                plot(ax, n_dense, fitted_props, ...
                    'Color',       c, ...
                    'LineWidth',   2, ...
                    'DisplayName', legend_label);
            else
                legend_label = sprintf('%s  (N=%d)  (insufficient data)', ...
                    qualifying_methods{method_idx}, method_variable_counts(method_idx));
                % Invisible dummy plot just to get a legend entry
                plot(ax, nan, nan, 'Color', c, 'LineWidth', 2, ...
                    'DisplayName', legend_label);
            end
        end

        legend(ax, 'TextColor', [0.89 0.91 0.94], ...
            'Color', [0.10 0.11 0.18], 'EdgeColor', [0.30 0.33 0.45]);
        title(ax, threshold_labels{thr_idx}, ...
            'Color', [0.89 0.91 0.94], 'FontSize', 10);
        xlabel(ax, 'Sample size (n)', 'Color', [0.89 0.91 0.94]);
        ylabel(ax, 'Edges above threshold (%)', 'Color', [0.89 0.91 0.94]);
        ylim(ax, [-2 105]);
    end

        sgtitle(sprintf('%s | %s | %s | test=%s\nProportion of Edges Above Power Threshold', ...
            upper(dataset), upper(map_type), task, test), ...
            'Color', [0.89 0.91 0.94], 'FontSize', 12, 'FontWeight', 'bold');
    
        exportgraphics(fig, fullfile(output_group_dir, 'edges_above_threshold.png'), ...
            'Resolution', 150, 'BackgroundColor', [0.06 0.07 0.10]);
        close(fig);
        fprintf('  [OK] Edges above threshold figure saved.\n');

    else
        fprintf('  [SKIP] No qualifying methods (>5 edges) found for threshold figure.\n');
    end

    % ── 4. HEATMAPS ───────────────────────────────────────────────────────
    for n_idx = 1:length(sample_sizes)
        current_n       = sample_sizes(n_idx);
        sample_size_key = sprintf('n%d', current_n);
        heatmap_dir     = fullfile(output_group_dir, sprintf('heatmaps_n%d', current_n));
        if ~exist(heatmap_dir, 'dir'), mkdir(heatmap_dir); end

        for method_idx = 1:length(EDGE_METHODS)
            method = EDGE_METHODS{method_idx};
            if ~isfield(condition_data, sample_size_key) || ~isfield(condition_data.(sample_size_key), method), continue; end

            power_matrix = unflatten_matrix(mask, 'flat_to_spatial', condition_data.(sample_size_key).(method));

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

            exportgraphics(fig, fullfile(heatmap_dir, sprintf('heatmap_%s.png', method)), ...
                           'Resolution', 150, 'BackgroundColor', [0.06 0.07 0.10]);
            close(fig);
        end
    end
    fprintf('  [OK] Heatmaps saved for n = [%s].\n', ...
        strjoin(arrayfun(@num2str, sample_sizes, 'UniformOutput', false), ', '));

    % ── 5. CSV EXPORT ─────────────────────────────────────────────────────

    % Edge groups and mask are the same for all n — write once
    writematrix(double(edge_groups), fullfile(output_group_dir, 'edge_groups.csv'));
    writematrix(double(mask),        fullfile(output_group_dir, 'mask.csv'));

    for n_idx = 1:length(sample_sizes)
        current_n        = sample_sizes(n_idx);
        sample_size_key  = sprintf('n%d', current_n);
        csv_output_dir   = fullfile(output_group_dir, sprintf('csv_n%d', current_n));
        if ~exist(csv_output_dir, 'dir'), mkdir(csv_output_dir); end

        summary_rows = {};
        for method_idx = 1:length(EDGE_METHODS)
            method = EDGE_METHODS{method_idx};
            if ~isfield(condition_data, sample_size_key) || ~isfield(condition_data.(sample_size_key), method), continue; end

            power_matrix = unflatten_matrix(mask, 'flat_to_spatial', condition_data.(sample_size_key).(method));

            % Power matrix CSV
            writematrix(power_matrix, fullfile(csv_output_dir, sprintf('%s_power.csv', method)));

            % Accumulate calculation summary row
            summary_row = {method};
            for threshold_idx = 1:length(POWER_THRESHOLDS)
                power_threshold               = POWER_THRESHOLDS(threshold_idx);
                edges_above_threshold         = sum(power_matrix(:) > power_threshold) / 2;  % symmetric, count unique edges
                summary_row{end+1}            = edges_above_threshold; %#ok<SAGROW>
            end
            summary_rows{end+1} = summary_row; %#ok<SAGROW>
        end

        % Calculations summary CSV
        if ~isempty(summary_rows)
            summary_headers = [{'Method'}, arrayfun(@(t) sprintf('above_%d_pct', t), ...
                                POWER_THRESHOLDS, 'UniformOutput', false)];
            summary_table   = cell2table(vertcat(summary_rows{:}), 'VariableNames', summary_headers);
            writetable(summary_table, fullfile(csv_output_dir, 'calculations_summary.csv'));
        end
    end
    fprintf('  [OK] CSVs saved.\n');
end

fprintf('\nAll done! Outputs under: %s\n', output_root);