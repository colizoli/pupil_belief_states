function [hard, easy] = define_coherence(setup)
% ONE FILE for Behavioral_2AFC and fMRI_2AFC
        if setup.participant == 1 
            hard = 0.70;
            easy = 0.85;  
        elseif setup.participant == 2 
            hard = 0.70;
            easy = 0.85;
        elseif setup.participant == 3 
            hard = 0.61;
            easy = 0.76;
        elseif setup.participant == 4 
            hard = 0.69;
            easy = 0.84;
        elseif setup.participant == 5 
            hard = 0.70;
            easy = 0.85;
        elseif setup.participant == 6 
            hard = 0.66;
            easy = 0.81;
        elseif setup.participant == 7 
            hard = 0.72;
            easy = 0.87;
        elseif setup.participant == 8 
            hard = 0.74;
            easy = 0.89;
        elseif setup.participant == 9 
            hard = 0.74;
            easy = 0.89;
        elseif setup.participant == 10 
            hard = 0.68;
            easy = 0.83;
        elseif setup.participant == 11 
            hard = 0.70;
            easy = 0.85;
        else
            hard = 0.70;
            easy = 0.85;
        end
end
