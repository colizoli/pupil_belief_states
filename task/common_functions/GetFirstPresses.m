% 
% for i = 1: length(firstPress)
%     
%     save = find(firstPress{i});
%     if save
%         disp(i);   % frame     
%         disp(save); % index of array in frame cell = key code
%         disp(firstPress{i}(save)); % secs of that key press
%     end
% 
% end
% 
% 

firstPress = results.firstPress;

c = 1;
for i = 1: length(firstPress)
    
    save = find(firstPress{i});
    if save
        disp(i);   % frame     
        disp(save); % index of array in frame cell = key code
        disp(firstPress{i}(save)); % secs of that key press
    
        frame(c) = i;
        key(c) = save;
        keyTime(c) = firstPress{i}(save);
        c = c + 1;
        
    end

end

