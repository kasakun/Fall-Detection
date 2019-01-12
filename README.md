# Fall Detecttion

### Author
Zeyu Chen

## ForeWord
The project is the final project of ECE 6258.

There are sevral parts of codes
Camera calibrtion is based on C++.
The Distance is based on MATLAB
The Preprocessing is based on Python 2.7.
The Detection System is based on Python 2.7. 
The openpose is based on C++ and caffe.  

If you only use video mode, openpose is not required since we provide test set for you to implement.

## Camera Calibration
To run this part, cmake is recommended.

Compile and Run:

```
$ cmake .
$ make
$ ./camera
```
The input images provided are in test_image directory.

## Preprocessing
The preprocessing consists of enhancement and background substraction.
There a two version of the script. One is one file processing, the other one is bach processing.

To run batch processing, create a directory named `video`, put all your videos into the directory.

## Detection System
Run
```
$ python falldetect2.5.py
```
To simply run in video mode, just put the input directory provided into the Detection directory and then set the video directory for the system.

System will send email to target address when fall detected. The default target email is chenzy@gatech.edu. The user can also change the email address.

If you want to run in real time version, several packages are required:
CUDA 8 (only)
cuDNN
OpenCV

The environment we use is Ubuntu 16

And you also need a ip camera in your local network and then input the ip address.

More details to use the tool can be found in the HELP in the software.

## Distance
When you change the camera or the scene, you should adjust the distance. In our method, we use curvefitting to get the map between head size and distance based on several measured points. Thus you can also generate your own map list by using the MATLAB code in this directory.

The edge_detector.m is used to preprocess the calibration images and extract the edge. After manually get the location of the diameter of head, spline_estimation.m is used to fit the curve.

## TEST VIDEO
In this directory we show all test videos we use.
In original directory, all videos are raw. If you want to start from the begining, you can use these videos.

First, do preprocessing, run Script in Preprocessing directory.

Then use openpose to extract key points information with command:
```
./build/examples/openpose/openpose.bin --no_display --write_images [video_name]/Image/ --write_keypoint_json [video_name]/Data --video [your video address]"
```
Then you will have a folder including processed data. Move it into Detection directory to test.

In the processed directory, all videos have been aleady preprocesing and key points are extracted. You do not need to reinstall the openpose and its environment. Just put the video directory into the Detection directory and then run video mode to retest the result.

_The test videos:https://www.dropbox.com/sh/skwk7cbkh82rrhw/AADniBuGf6WU7tgmzCIGPOFUa?dl=0_

