function method_level = find_method_level( ...
    power_by_method, ...
    n_variables, ...
    edge_groups, ...
    ALL_METHODS ...
)
% Manual type detection because not all result files carry an explicit
% method-level field. Infers level from the column count of each method's
% power matrix: full variable space, network space, or a single whole-brain value.

    % Number of networks (drop NaN; subtract 1 to exclude the 0 / unassigned label)
    n_nets = numel(unique(edge_groups(~isnan(edge_groups)))) - 1;

    method_level = struct();

    for method_idx = 1:length(ALL_METHODS)
        method = ALL_METHODS{method_idx};
        n = size(power_by_method.(method), 2);

        if n == n_variables
            method_level.(method) = 'variable';
        elseif n == n_nets
            method_level.(method) = 'network';
        elseif n == 1
            method_level.(method) = 'whole_brain';
        else
            error('find_method_level:unknownLevel', ...
                  ['Method "%s" has %d columns, which matches none of: ' ...
                  '        variable (%d), network (%d), or whole-brain (1).'], ...
                  method, n, n_variables, n_nets);
        end
    end
    
end