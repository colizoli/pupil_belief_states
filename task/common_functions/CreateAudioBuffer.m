function [buffer,loop] = CreateAudioBuffer(varargin)
% creates an audio buffer

try
    buffer = cat(2,varargin{:});

    loop = zeros(length(varargin),2);
    loop(1,:) = [0,size(varargin{1},2)-1];
    
    for i = 2:length(varargin)
        loop(i,:) = loop(i-1,2)+[1,size(varargin{i},2)];
    end % end of the for loop
    
catch % if something went wrong with the CreateAudioBuffer function, do the following
    % ShowCursor;
    disp('CreateAudioBuffer failed!');
    Screen('CloseAll');
    commandwindow;
    
    
end % end of the try-catch function
end % end of the CreateAudioBuffer function