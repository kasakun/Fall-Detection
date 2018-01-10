%% this codes is used to processing the photos which used in the distance measurement

I = imread('8.jpg');
I_gray = rgb2gray(I);

w=fspecial('gaussian',[5 5],3);
I_blur=imfilter(I_gray,w); %%smooth the image 

%%extracted the edge of the smoothed image to manually count the diameter of the head 
I_edged = edge(I_blur,'canny');  
figure, imshow (I_edged)
