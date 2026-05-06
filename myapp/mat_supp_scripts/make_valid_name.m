function valid_name = make_valid_name(str)

    % Replace any non-alphanumeric character with underscore
    valid_name = regexprep(str, '[^a-zA-Z0-9]', '_');

    % Must start with a letter — prefix x if it starts with digit or underscore
    if ~isempty(valid_name) && ~isletter(valid_name(1))
        valid_name = ['x' valid_name];
    end

end
