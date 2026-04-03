function s = json_to_struct(filepath)
% JSON_TO_STRUCT  Read a JSON file and decode it into a MATLAB struct.
%
%   s = json_to_struct(filepath)
%
%   filepath - path to a JSON file, e.g. 'data/index.json'
%   s        - decoded struct (nested as per JSON structure)
%
%   Notes:
%     - JSON arrays of objects become struct arrays.
%     - JSON arrays of scalars become numeric arrays.
%     - Keys that are not valid MATLAB identifiers are preserved as-is by
%       jsondecode (it replaces illegal chars with underscores).

    if ~isfile(filepath)
        error('json_to_struct: file not found: %s', filepath);
    end

    fid = fopen(filepath, 'r', 'n', 'UTF-8');
    if fid == -1
        error('json_to_struct: could not open file for reading: %s', filepath);
    end

    raw = fread(fid, '*char')';
    fclose(fid);

    s = jsondecode(raw);
end