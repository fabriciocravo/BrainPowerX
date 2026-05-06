function method_plot_name = map_method_name_to_plot_name(method_name)

  switch method_name

  case 'Parametric_FWER'
    method_plot_name = 'Edge FWER';
  case 'Parametric_FDR'
    method_plot_name = 'Edge FDR';
  case 'Size'
    method_plot_name = 'Cluster Size';
  case 'Fast_TFCE'
    method_plot_name = 'Cluster TFCE';
  case 'Constrained_FWER'
    method_plot_name = 'Network FWER';
  case 'Constrained_FDR'
    method_plot_name = 'Network FDR';
  case 'Omnibus_Multidimensional_cNBS'
    method_plot_name = 'Whole-Brain cNBS';
  otherwise
    error('Method not supported: %s', method_name);

  endswitch


end
