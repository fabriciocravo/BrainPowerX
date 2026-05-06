function result = fit_power_curve(ns, proportions, varargin)

    % Guarantee dimentional consistency
    ns = ns(:);
    proportions  = proportions(:);

    p = inputParser;
    default_func = @(params, x) params(3) ./ (1 + (params(1) ./ x).^params(2));
    addParameter(p, 'fit_function', default_func, @(x) isa(x, 'function_handle'));
    addParameter(p, 'lower_bounds', [1, 0.1, 0],         @isnumeric);
    addParameter(p, 'upper_bounds', [100000, 5, 100],     @isnumeric);
    parse(p, varargin{:});

    power_func = p.Results.fit_function;
    lb = p.Results.lower_bounds;
    ub = p.Results.upper_bounds;

    initial_params = [median(ns), 1, 50];
    cost_func      = @(params) sum((proportions - power_func(params, ns)).^2);

     try
        if exist('OCTAVE_VERSION', 'builtin')
            % Octave version
            fitted_params = sqp(initial_params, cost_func,
              [], [], lb, ub ...
            );

        else
            % MATLAB
            options = optimoptions('fmincon', ...
                'Display',                'off', ...
                'MaxFunctionEvaluations', 10000, ...
                'MaxIterations',          5000, ...
                'OptimalityTolerance',    1e-8, ...
                'StepTolerance',          1e-10, ...
                'Algorithm',              'interior-point');
            fitted_params = fmincon(cost_func, initial_params, [], [], [], [], lb, ub, [], options);
        end

        result.P = fitted_params(3);
        result.a = fitted_params(1);
        result.b = fitted_params(2);

    catch e
        error('Curve fit failed: %s', e.message);
    end

end
