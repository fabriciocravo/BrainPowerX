function quantile_average = get_quantile_average_power( ...
    quantile_percentage, ...
    power_by_method, ...
    sample_sizes, ...
    method_level, ...
    proportion_level, ...
    ALL_METHODS ...
)
       %%
% This function calculates the average power for a given brain quantile
% percentage by taking the highest power values until the brain
% quantile percentage is satisfied
    %%
% Inputs:
%   quantile_percentage - target brain proportion to cover (fraction, 0-1).
%                         e.g. 0.1 keeps the highest-power variables until
%                         the top 10% of the brain is accounted for
%   power_by_method     - struct keyed by method name; each field is a
%                         matrix (rows = sample sizes, cols = variables)
%   sample_sizes        - vector of sample sizes, aligned to the rows of
%                         each power_by_method matrix
%   method_level        - struct keyed by method name; value is the level
%                         token ('variable', 'network', or 'whole_brain')
%   proportion_level    - struct with fields 'variable'/'network'/
%                         'whole_brain'; each a vector of per-variable
%                         brain proportions, indexed to match the columns
%                         of the corresponding power matrix
%   ALL_METHODS         - cell array of method names to iterate over
%
% Output:
%   quantile_average    - struct keyed by method name; each field is a
%                         vector (1 x n_sample_sizes) of average power over
%                         the selected top-quantile slice
%%
    
    quantile_average = struct();

    for method_idx = 1:length(ALL_METHODS)
        method = ALL_METHODS{method_idx};

        % power_by_method struct is accessed with the method name
        % Get the power for a method - all sample sizes
        method_power = power_by_method.(method);

        % Each variable's brain proportion, matching the columns of method_power
        level = method_level.(method);
        proportions = proportion_level.(level);
        
        average_by_n = nan(1, length(sample_sizes));

        for n_idx = 1:length(sample_sizes)
            
            % For the power for an specific sample size
            % simply use the matching index to get the correct row
            power_row = method_power(n_idx, :);
    
            % For each row, sort the power
            % Keep original index
            [sorted_power, sort_idx] = sort(power_row, 'descend');
    
            % Start accumulator as zero
            accumulated_proportion = 0;
            n_selected = 0;
    
            % while the accumulator has not passed the quantile_percentage
            % add one more variable
            while accumulated_proportion < quantile_percentage
                n_selected = n_selected + 1;
    
                % If all variables are selected, use them and break
                if n_selected > numel(sorted_power)
                    n_selected = numel(sorted_power);
                    break
                end
    
                accumulated_proportion = accumulated_proportion + ...
                    proportions(sort_idx(n_selected));
            end
          
            % Once done - calculate average power
            average_by_n(n_idx) = mean(sorted_power(1:n_selected));
        end
    
        % Store in struct with method name 
        quantile_average.(method) = average_by_n;
    end

end