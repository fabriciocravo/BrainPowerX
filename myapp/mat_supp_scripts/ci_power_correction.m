function power_by_method = ci_power_correction( ...
    power_by_method, ...
    grouped_data, ...
    method_level, ...
    ALL_METHODS ...
)

% Get necessary things from grouped data
n_reps      = grouped_data.n_reps;
edge_groups = grouped_data.edge_groups;

network_labels = edge_groups(~isnan(edge_groups));     % drop masked entries
network_labels = network_labels(network_labels > 0);   % drop 0 / unassigned
n_nets = numel(unique(network_labels));

P_FAIL = 0.05; % shared target failure probability across all levels

% --- Level-specific alpha ---
% 'variable': FCP bound derived for ~35,778 edges, giving 0.95 coverage
%             at 0.05 failure probability (see Theorem 1 derivation).
ALPHA_VARIABLE = 0.00013;

% 'network': only up to 55 networks, so a Bonferroni FWER correction
%            across n_nets tests is sufficient (and much less
%            conservative than the edge-level FCP bound).
ALPHA_NETWORK = P_FAIL / n_nets;

% 'whole_brain': single estimate, no multiplicity/selection to correct
%                for, so uncorrected one-sided 0.05.
ALPHA_WHOLE_BRAIN = P_FAIL;
    
    for m_idx = 1:numel(ALL_METHODS)
        method = ALL_METHODS{m_idx};
    
        switch method_level.(method)
            case 'variable'
                z = norminv(1 - ALPHA_VARIABLE);
            case 'network'
                z = norminv(1 - ALPHA_NETWORK);
            case 'whole_brain'
                z = norminv(1 - ALPHA_WHOLE_BRAIN);
        end
    
        p_hat = power_by_method.(method) / 100; % convert to fraction
        se    = sqrt(p_hat .* (1 - p_hat) / n_reps);
        lower = p_hat - z .* se;
        lower = max(lower, 0); % clip at 0
        power_by_method.(method) = lower * 100; % back to percent
    end

end