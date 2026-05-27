function result = unflatten_matrix(data, mask, map_type)

    switch map_type

        case 'act'
          volume = zeros(size(mask));
          volume(mask) = data;
          result = volume;

        case 'fc'
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
