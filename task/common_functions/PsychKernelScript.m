% in an OSX terminal run:

cd /System/Library/Extensions/
sudo unzip /Applications/Psychtoolbox/PsychHardware/PsychtoolboxKernelDriver64Bit.kext.zip


% On modern OSX systems, this will automatically load the driver after a
%   few seconds, and also after each system restart. On older systems you
%   have to load the driver manually - on new systems you could do this for
%   debugging purposes: How to enable (each time after restarting your system):
%  
%   In a terminal type:
  sudo kextload /System/Library/Extensions/PsychtoolboxKernelDriver.kext