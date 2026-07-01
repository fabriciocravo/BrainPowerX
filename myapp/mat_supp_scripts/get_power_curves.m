function curve_fits = get_power_curves( ...
    quantile_average, ...
    sample_sizes, ...
    ALL_METHODS ...
)

    curve_fits = struct();
    for method_idx = 1:length(ALL_METHODS)

        method          = ALL_METHODS{method_idx};
        mean_power_by_n = quantile_average.(method);

        if numel(mean_power_by_n) >= 3
            curve_fits.(method) = fit_power_curve(sample_sizes, mean_power_by_n);
        else
            error('A curve fit did not have enough values')
        end

    end

end