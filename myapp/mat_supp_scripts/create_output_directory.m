function output_group_dir = create_output_directory(output_group_dir)
    if ~exist(output_group_dir, 'dir')
        mkdir(output_group_dir)
    end
end