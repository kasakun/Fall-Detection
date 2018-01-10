#
# Author:Yijun Zhang
#        Zeyu Chen

# This is the batch version of preprocessing.
# data_path is the directory of target videos
import cv2
import os
import numpy as np
import skvideo.io as sv



data_path = './video/'
index = 1
for fn in os.listdir(data_path):
    cap = sv.VideoCapture(data_path + fn)
    print cap.isOpened()
    print data_path + fn
    outname = 'sub_bg' + str(index) + '.mp4'
    out = sv.VideoWriter(outname, 'H264', 30.0, (640, 480), True)
    out.open()
    ret, frame2 = cap.read()
    current_frame = frame2


    ## extract background
    fgbg = cv2.createBackgroundSubtractorKNN()

    while True:
        ret, frame = cap.read()    
        try:
            frame.any() 
        except AttributeError:
            break
        b, g, r = cv2.split(frame)
        ori_frame = frame
        ori_frame = cv2.merge([r, g, b])
        cv2.imshow('frame', ori_frame) ## the frame we get from the camera 
        # Edge Enhancement 
        b, g, r = cv2.split(frame)
        b_gray = cv2.GaussianBlur(b, (5, 5), 0)
        b_edged = cv2.Canny(b_gray, 35, 125)
     
        g_gray = cv2.GaussianBlur(g, (5, 5), 0)
        g_edged = cv2.Canny(g_gray, 35, 125)
     
        r_gray = cv2.GaussianBlur(r, (5, 5), 0)
        r_edged = cv2.Canny(r_gray, 35, 125)
        
        edge_frame = cv2.merge([b + 0.1*b_edged, g + 0.1*g_edged, r + 0.1*r_edged])

        
        b, g, r = cv2.split(frame)
        ## using equalizehist to adjust the constrast of the image 
        b = cv2.equalizeHist(b)
        g = cv2.equalizeHist(g)
        r = cv2.equalizeHist(r)

        frame = cv2.merge([b, g, r])

        fmask = fgbg.apply(frame)
    
        # denosing the area of motion  
        th = cv2.threshold(fmask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
        th = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
        dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 3)), iterations=2)


        # if it is a stationary video, define the number 
        nonzeroNum = np.count_nonzero(dilated)
        if nonzeroNum == 0:
            min_x1 = 1
            max_x1 = 1
            min_y1 = 2
            max_y1 = 2
        else: 
            x1, y1 = np.nonzero(dilated)
            min_x1 = x1.min()+1
            max_x1 = x1.max()+1
            min_y1 = y1.min()+2
            max_y1 = y1.max()+2 

        # compute the minimal rect of motion area
        c = np.array([[max_y1,min_x1],[max_y1,max_x1],[min_y1,min_x1],[min_y1,max_x1]]) 
        rect = cv2.minAreaRect(c)
        box = np.int0(cv2.boxPoints(rect))
        

        ##  fill the motion area 
        cv2.drawContours(dilated, [box], -1, (0, 255, 0), 3)
        image1 = cv2.fillPoly(dilated, [box], (255, 255, 255));  

        ##  extract the motion area
        
        b, g, r = cv2.split(frame)

        res_b = b*(image1/255)
        res_g = g*(image1/255)
        res_r = r*(image1/255)
        ## merge the image 
        result = cv2.merge([res_r, res_g, res_b])
        realresult = cv2.merge([res_b, res_g, res_r])
        cv2.imshow('result', result) ## the motion area 
        out.write(realresult)

        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break
    print fn + ' finished...'
    cap.release()

    index = index + 1
