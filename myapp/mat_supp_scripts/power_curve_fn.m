function y = power_curve_fn(n, P, a, b)
%POWER_CURVE_FN  P / (1 + (a/n)^b)
    y = P ./ (1 + (a ./ n) .^ b);
end