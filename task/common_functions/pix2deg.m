function ang = pix2deg(display,pix)

%angle = pix2angle(display,pix)
%
%converts monitor pixels into degrees of visual angle.
%
%Inputs:
%display.dist (distance from screen (cm))
%display.width (width of screen (cm))
%display.resolution (number of pixels of display in horizontal direction)
%
%ang (visual angle)
%
%Warning: assumes isotropic (square) pixels

%Written 11/1/07 gmb zre

%Calculate pixel size
pixSize = display.width/display.res.width;   %cm/pix

sz = pix*pixSize;  %cm (duh)

ang = 2*180*atan(sz/(2*display(1).dist))/pi;


return

%test code

display.dist = 60; %cm
display.width = 44.5; %cm
display.resolution = [1680,1050];

pix = 100;

ang = pix2angle(display,pix)