function find_method_level( ...
    power_by_method, ...
    n_variables, ...
    edge_groups, ...
    ALL_METHODS ...
)
    
    % I had to code a manual type find because not all resulting files are
    % updated ....
    % This just 
    
    % Get number of networks
    n_nets = numel(unique(edge_groups(~isnan(edge_groups)))) - 1;
    
    % Struct that stores the level of each method
    method_level = struct();

    for method_idx = 1:length(ALL_METHODS)
        method = ALL_METHODS{method_idx};
    
        n = size(power_by_method.(method), 2)

        switch n

            case n == n_variables
                method_level = ''
    end


end