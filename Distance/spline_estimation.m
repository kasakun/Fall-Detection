clc;
close all;
clear all;

%% the location of pixels of head which manually count from  edge_detector
A = [284 , 295, 303, 306, 310, 311]
B = [350, 342, 339, 337, 337, 334]
C = B-A

%% the inches from the camera to the people
SS = [60,80,100,120,140,160]

%% match the curve using spline fit
xx = 1:680;
yy = spline(C,SS,xx);
figure, plot(C,SS,'o',xx,yy)

%% remove the unreasonable points
for xx=1:680
    result(xx) = yy(xx);
    if yy(xx) <=0
        result(xx) = 0;
    end
end
save ('distance_pixel.mat','result')

