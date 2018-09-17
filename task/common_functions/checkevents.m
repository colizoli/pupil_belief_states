function [ results ] = checkevents( blockbegin, trial, setup, results )
% function [ results, noise ] = checkevents( blockbegin, trial, setup, results, noise )

         %-------------
         % Check for pulses and accidental key presses and logs them in
         % 'scannerpulses' and 'nonpulse' respectively
         %-------------
         if isempty(trial), trial = 0; end
         
            [ pressed, firstPress, firstRelease ]=KbQueueCheck; % Collect keyboard events since KbQueueStart was invoked
            if pressed
                pressedCodes=find(firstPress); % which key
%                 disp(pressedCodes);
%                 disp(firstPress);
%                 disp(size(pressedCodes));
                if pressedCodes == 23; 
                    for i=1:size(pressedCodes,2)
                        results.pulsecount = results.pulsecount + 1;
                        results.scannerpulses.key(results.pulsecount) = KbName(pressedCodes(i)); % char(pressedCodes(i)) to see which key
                        results.scannerpulses.trialtime(results.pulsecount) = firstPress(pressedCodes(i))-blockbegin;
                        results.scannerpulses.seconds(results.pulsecount) = firstPress(pressedCodes(i));
                        if setup.Eye                        
                            Eyelink ('Message', sprintf('trial %i event <EVENT(2-KeyDown {scancode:17, key: 116, unicode:ut, mod: 0})> at %d', ... 
                                trial, results.scannerpulses.seconds(results.pulsecount)));
                        end
                    end
                else % accidental key press
                    for i=1:size(pressedCodes,2)
                        results.presscount = results.presscount + 1;
                        results.nonpulse.key{results.presscount} = KbName(pressedCodes(i)); % to see which key
                        results.nonpulse.trialtime(results.presscount) = firstPress(pressedCodes(i))-blockbegin;
                        results.nonpulse.seconds(results.presscount) = firstPress(pressedCodes(i));
                        if setup.Eye                        
                            Eyelink ('Message', sprintf('trial %d event <EVENT(2-KeyDown Accident {scancode:, key: %i, unicode:, mod: 0})> at %d', ...
                                trial, pressedCodes(i), results.nonpulse.seconds(results.presscount)));
                        end
                    end    
                end % if t 23
            end % pressed
end
