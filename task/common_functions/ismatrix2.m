% True if the specified value represents a matrix.
% The property browser opens the matrix editor for modifying the value of
% a matrix.
%
% See also: isscalar, isvector

% Copyright 2008-2009 Levente Hunyadi
function tf = ismatrix2(value)

tf = ndims(value) == 2 && length(value) > 1;

end