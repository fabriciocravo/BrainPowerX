function proportion_level = get_brain_variable_proportion( ...
    n_var, ...
    edge_groups ...
)

    % Define an empty struct proportion of method struct
    % The struct has the filds (variable, network, whole_brain)
    % Each field contains an indexed vector 1,n_level
    % Each element of this vector contains the corresponding brain
    % proportion of the respective variable (indexes must match)

    proportion_level = struct();

    % For variable level each variable corresponds to an uniform percentage
    proportion_level.variable = (1 / n_var) * ones(1, n_var);

    % For a network, the proportion of indexes equal to the proportion of
    % times that index appears in edge_groups
    network_labels = edge_groups(~isnan(edge_groups));     % drop masked entries
    network_labels = network_labels(network_labels > 0);   % drop 0 / unassigned
    n_nets = numel(unique(network_labels));

    network_proportion = zeros(1, n_nets);
    for net_idx = 1:n_nets
        network_proportion(net_idx) = ...
            sum(network_labels == net_idx) / numel(network_labels);
    end
    proportion_level.network = network_proportion;

    % For whole_brain - it's simply 1
    proportion_level.whole_brain = 1;

end