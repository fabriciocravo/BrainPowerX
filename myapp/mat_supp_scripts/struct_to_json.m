function struct_to_json(s, filepath)
% STRUCT_TO_JSON  Encode a struct and write it to a JSON file.
%
%   struct_to_json(s, filepath)
%
%   s        - any MATLAB struct (nested structs and arrays are supported)
%   filepath - destination path, e.g. 'data/index.json'
%
%   Notes:
%     - jsonencode produces compact JSON by default.
%     - PrettyPrint adds indentation (R2021a+).

    json_str = jsonencode(s, 'PrettyPrint', true);

    fid = fopen(filepath, 'w', 'n', 'UTF-8');
    if fid == -1
        error('struct_to_json: could not open file for writing: %s', filepath);
    end

    fprintf(fid, '%s', json_str);
    fclose(fid);

    fprintf('Written: %s\n', filepath);
end