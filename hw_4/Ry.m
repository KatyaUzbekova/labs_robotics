function [Ry] = Ry(t)
    Ry = [cos(t) 0 sin(t) 0; 0 1 0 0; -sin(t) 0 cos(t) 0; 0 0 0 1];
end