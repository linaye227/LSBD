% Demo to simulate a bouncing ball.
clc;    % Clear the command window.
fprintf('Beginning to run %s.m.\n', mfilename);
close all;  % Close all figures (except those of imtool.)
clear;  % Erase all existing variables. Or clearvars if you want.
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 20;
H0 = 10+(30-10)*rand(1,20);
%h0 = 20;	% Initial drop height in meters.
v = 0;		% Initial y velocity in m/sec.
g = 9.8;	% Gravitational acceleration in m/s^2;
t = 0;		% Initial time when dropped
dt = 0.01;	% Delta time in seconds.
rho = 0.75;	% Velocity reduction factor.  Velocity reduces this much after a bounce.
%peakHeight = h0;	% Initial drop height in meters.
%h = h0;		% Instantaneous height.
hstop = 0.001;	% Height at which if the peak height after a bounce is less than this, stop the simulation.
% Preallocate arrays for time and height.  Make them plenty large - we will crop to the final size later.
T = 0 : dt : 1000;
H = zeros(1, length(T));
% Setup a failsafe.  Don't do more than this number of iterations or else we might have an infinite loop.  This will prevent that.
maxIterations = 1000000;		
loopCounter = 1;
iniHeightCounter=0;
while(iniHeightCounter<20)
    iniHeightCounter=iniHeightCounter+1;
    loopCounter = 1;
    H = zeros(1, length(T));
    peakHeight = H0(iniHeightCounter);	% Initial drop height in meters.
    h = H0(iniHeightCounter);		% Instantaneous height.
    while (peakHeight > hstop) && (loopCounter < maxIterations)
	% Compute new height.
        hNew = h + v * dt - 0.5 * g * dt ^ 2;
	% 	fprintf('After iteration %d, time %f, hmax = %f.\n', loopCounter, T(loopCounter), hNew);
        if(hNew<0)
		% Ball hit the ground.
% Find index of last time h was 0
            lastBounceIndex = find(H(1: loopCounter-1) == 0, 1, 'last');
            if isempty(lastBounceIndex)
			% If it hasn't bounced yet, start looking from the beginning.
                lastBounceIndex = 1;
            end
		% Compute the greatest height since the last bounce, or the initial release.
            [peakHeight, index] = max(H(lastBounceIndex : end)); % Record height
% Find time when it was at that height.
            tMax = T(index + lastBounceIndex - 1);
            plot(tMax, peakHeight, 'b+', 'MarkerSize', 18, 'LineWidth', 2);
            hold on;
            fprintf('After tour %d, iteration %d, time %f, hmax = %f.\n', iniHeightCounter, loopCounter, tMax, peakHeight);
		
		% Reflect it up.  For example, if at this time,
% the ball was going to be at -4 (with no ground in the way)
% Now, after bouncing, it would be at +4 above the ground.
            h = 0; %abs(hNew);
            v = -v * rho;
		
        else
		% Ball is falling or rising.
            v = v - g*dt;
            h = hNew;
        end
        H(loopCounter) = h;
        loopCounter = loopCounter + 1;
    end


% Crop times.
%save('BB1.mat','T','H')
    %T = T(iniHeightCounter,:);
    %H = H(iniHeightCounter,:);
    if exist('BB.mat','file')
        %dataCell = [name,num2cell(trez),num2cell(score)];
        save('BB.mat', '-append','T','H');
    else
         
        save('BB.mat','T','H');
    end
% Plot the trajectory.

end

save('BBcomplete.mat','T','H')


plot(T, H, 'r.', 'MarkerSize', 5);
grid on;
xlabel('Time [seconds]', 'FontSize', fontSize)
ylabel('Ball Position Y [m]', 'FontSize', fontSize)
title('Bouncing Ball', 'FontSize', fontSize)
% Maximize window
g = gcf;
g.WindowState = 'maximized';
fprintf('Done running %s.m.\n', mfilename);