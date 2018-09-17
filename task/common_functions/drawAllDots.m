function [ display ] = drawAllDots(display, dots, block, trial, stimuli, frameNum)

% draws the dots on the screen for this frame
Screen('DrawDots',display.h,squeeze(stimuli(block, trial, frameNum, :, :)), ...
    dots.size, dots.color, display.center, 2);

end