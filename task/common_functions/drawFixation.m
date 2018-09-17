function [ display ] = drawFixation( display, dots, fix )
% Fixation
% shape of the ABC (figure 1) in:
% Thaler, L., Sch?tz, a C., Goodale, M. a, & Gegenfurtner, K. R. (2013). 
% What is the best fixation target? The effect of target shape on stability
% of fixational eye movements. Vision research, 76, 31?42.

X = display.center(1);
Y = display.center(2);

% NOTE: In order to control for luminance, 
% the surface area (SA) of the inside circle should equal 
% the SA outside circle - SA inside circle. 
% i.e. A - B = B, where A and B are the surface areas of the outside and inside
% circles, respectively. 
% Therefore, this has ratio has to be held constant! 
if fix.flip 
    r1 = [0 0 72 96];
    r2 = [0 0 48 72];
else
    r1 = [0 0 96 72];
    r2 = [0 0 72 48];
end

r1 = r1./3;
r2 = r2./3;

r1 = CenterRectOnPoint(r1,X,Y);
r2 = CenterRectOnPoint(r2,X,Y);

% cover the inner space for any stray dots
% Screen('FillOval', display.h, display.black, [display.center(1)-dots.innerspace, ...
%     display.center(2)- dots.innerspace*.8, display.center(1)+dots.innerspace*.8, display.center(2)+dots.innerspace*.8], ...
%     dots.innerspace*.8); 

Screen('FillOval', display.h, [118 118 118], [display.center(1)-dots.innerspace, ...
     display.center(2)- dots.innerspace*.8, display.center(1)+dots.innerspace*.8, display.center(2)+dots.innerspace*.8], ...
     dots.innerspace*.8); 

Screen('FillRect', display.h, fix.color1, r1); % outside
Screen('FillRect', display.h, fix.color2, r2); % inside

end

