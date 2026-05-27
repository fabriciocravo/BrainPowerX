function color = map_method_name_to_color(method_name)

  switch method_name

  case 'Parametric_FWER'
    color = [0.40 0.76 0.95];   % light blue
  case 'Parametric_FDR'
    color = [0.20 0.50 0.85];   % blue
  case 'Size'
    color = [0.55 0.90 0.55];   % light green
  case 'Size_cpp'
    color = [0.55 0.90 0.55];   % light green
  case 'Size_Node_cpp'
    color = [0.55 0.90 0.55];   % light green
  case 'Fast_TFCE'
    color = [0.15 0.70 0.35];   % green
  case 'Fast_TFCE_cpp'
    color = [0.15 0.70 0.35];   % green
  case 'IC_TFCE_Node_cpp'
    color = [0.15 0.70 0.35];   % green
  case 'Constrained_FWER'
    color = [0.95 0.55 0.40];   % light orange-red
  case 'Constrained_cpp_FWER'
    color = [0.95 0.55 0.40];   % light orange-red
  case 'Constrained_FDR'
    color = [0.85 0.20 0.20];   % red
  case 'Constrained_cpp_FDR'
    color = [0.85 0.20 0.20];   % red
  case 'Omnibus_Multidimensional_cNBS'
    color = [0.80 0.50 0.95];   % purple
  case 'Omnibus_cNBS'
    color = [0.80 0.50 0.95];   % purple
  otherwise
    error('Method not supported: %s', method_name);

  endswitch

end
