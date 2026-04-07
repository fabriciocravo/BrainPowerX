function result = unflatten_matrix(data, mask, varargin)

    p = inputParser;
    addRequired(p, 'data');
    addRequired(p, 'mask');
    addParameter(p, 'variable_type', 'edge', @ischar);
    parse(p, data, mask, varargin{:});

    variable_type   = p.Results.variable_type;

    switch variable_type

        case 'edge'    
            % Called with data — return matrix directly

            fprintf('  [unflatten_matrix] data: %d elements | mask: %d x %d (%d true)\n', ...
                numel(data), size(mask, 1), size(mask, 2), sum(mask(:)));
            result = roi_roi_unflat(data, mask);

        otherwise
            error('unflatten_matrix: variable_type ''%s'' not yet supported.', ...
                variable_type);
            
    end

end

function unflat_matrix = roi_roi_unflat(flat_matrix, mask)
    temp_y          = zeros(size(mask));
    temp_y(mask)    = flat_matrix;
    unflat_matrix   = temp_y + temp_y';
end