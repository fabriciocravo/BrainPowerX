function power_matrix = unflatten_network(network_power, edge_groups)
% Projects network-level power values into edge space, then unflattens to square matrix.
% network_power : (n_networks x 1) power value per network
% edge_groups   : (n_edges x 1)   network index for each edge
% mask          : logical square matrix defining edge positions
    
    % Retriving network values
    edge_power = zeros(size(edge_groups));          
    assigned   = edge_groups > 0;              
    edge_power(assigned) = network_power(edge_groups(assigned));  
    
    % Simetry
    power_matrix = edge_power + edge_power';
    
end