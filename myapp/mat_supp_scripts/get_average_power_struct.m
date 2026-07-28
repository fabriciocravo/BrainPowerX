    function [power_by_method, sample_sizes] = get_average_power_struct( ...
          grouped_data, ...
          ALL_METHODS ...
        )
    
        % Collect sorted sample sizes from n* fields
        grouped_data_fields = fieldnames(grouped_data);
    
        is_sample_size_field  = startsWith(grouped_data_fields, 'n') & ...
                                cellfun(@(x) ~isnan(str2double(x(2:end))), ...
                                grouped_data_fields);
    
        sample_sizes          = sort(cellfun(@(x) str2double(x(2:end)), ...
            grouped_data_fields(is_sample_size_field)));
    
        % ------ AVERAGE POWER CALCULATION AND FIGURES
        power_by_method = struct();
    
        for method_idx = 1:length(ALL_METHODS)
            method = ALL_METHODS{method_idx};
        
            % number of variables for THIS method (peek at first sample size)
            first_key = sprintf('n%d', sample_sizes(1));
            n_vars    = numel(grouped_data.(first_key).(method));
        
            % rows = sample sizes, cols = variables
            power_matrix = nan(length(sample_sizes), n_vars);
        
            for n_idx = 1:length(sample_sizes)
                sample_size_key = sprintf('n%d', sample_sizes(n_idx));
                power_matrix(n_idx, :) = grouped_data.(sample_size_key).(method);
            end
        
            power_by_method.(method) = power_matrix;
        end
    
    end
