function result = fit_power_curve(ns, powers)
%FIT_POWER_CURVE  Fits P / (1 + (a/n)^b) to observed (ns, powers) data.
%   Returns struct with fields P, a, b or empty if fit fails.

    result = [];
    try
        ft   = fittype('P / (1 + (a/n)^b)', 'independent', 'n', ...
                       'coefficients', {'P', 'a', 'b'});
        opts = fitoptions(ft);
        opts.Lower      = [0,    0,   0.1];
        opts.Upper      = [100,  1e4, 20 ];
        opts.StartPoint = [100,  median(ns), 2];
        opts.MaxIter    = 1000;

        fitted        = fit(ns(:), powers(:), ft, opts);
        result.P      = fitted.P;
        result.a      = fitted.a;
        result.b      = fitted.b;
    catch e
        fprintf('    [WARN] Curve fit failed: %s\n', e.message);
    end
end