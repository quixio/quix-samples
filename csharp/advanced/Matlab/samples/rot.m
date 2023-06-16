function M = rot(v, theta)
    R = [cos(theta) -sin(theta); sin(theta) cos(theta)];
    M = R * v;
end