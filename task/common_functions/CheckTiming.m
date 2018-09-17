
% phase 1 - baseline period
% phase 2 - pre trial period (wait for trigger)
% phase 3 - stimulus on period (750 ms)
% phase 4 - stim offset -> response
% phase 5 - response -> feedback
% phase 6 - ITI after feedback

t = results.outputPhase - BEGIN;

p1 = t(1,2) - t(1,1) % baseline
p2 = t(1,3) - t(1,2) % trigger
p3 = t(1,4) - t(1,3) % stim
p4 = t(1,5) - t(1,4) % response
p5 = t(1,6) - t(1,5) % feedback

p3 = t(2,4) - t(2,3) % stim
p3 = t(3,4) - t(3,3) % stim


size(flip.stim.StimOns,1)

flip.stim.StimOns(end,1) - flip.stim.StimOns(1,1)