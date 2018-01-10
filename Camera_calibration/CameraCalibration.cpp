//
// Author: Zeyu Chen, based on opencv example
//
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/calib3d/calib3d.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace cv;
using namespace std;

int main() 
{
	ifstream fin("calibdata.txt");                  //Listof Imput Images
	ofstream fout("caliberation_result.txt");       //Output Calibration result
	//Extracting Corners in sub pixel 	
	cout<<"Start extracting the  corner  point...";
	int image_count=0;                             //Image Counter
	Size image_size;                               //Image Size
	Size board_size = Size(5,7);                   //Number of Chessboard Corners ()
	vector<Point2f> image_points_buf;              //Buffer for Corners of each Image
	vector<vector<Point2f> > image_points_seq;     //Save all Corners
	string filename;
	int count= -1 ;                                //Counter of  corners
	while (getline(fin,filename))
	{
		image_count++;		
		// Number of Image
		cout<<"image_count = "<<image_count<<endl;		
		// Check  Output
		cout<<"-->count = "<<count<<endl;	
		cout<< filename <<count<<endl;	
		Mat imageInput=imread(filename);
		// Use the first pic to get size of the image
		if (image_count == 1)                        
		{
			image_size.width = imageInput.cols;
			image_size.height =imageInput.rows;			
			cout<<"image_size.width = "<<image_size.width<<endl;
			cout<<"image_size.height = "<<image_size.height<<endl;
		}

		//Extracting Corners
		if (0 == findChessboardCorners(imageInput,board_size,image_points_buf))
		{			
			cout<<"can not find chessboard corners!\n"; // Corners not found
			exit(1);
		} 
		else 
		{
			Mat view_gray;
			cvtColor(imageInput,view_gray,CV_RGB2GRAY);
			// Achieve accuracy  of sub  pixel
			find4QuadCornerSubpix(view_gray,image_points_buf,Size(5,5)); 
			// Save Sub pixel
			image_points_seq.push_back(image_points_buf);  
			// Mark the corners on the image
			drawChessboardCorners(view_gray,board_size,image_points_buf,true); 
			imshow("Camera Calibration",view_gray);
			//  Pause
			waitKey(500);	
		}
	}
	int total = image_points_seq.size();
	cout<<"total = "<<total<<endl;
	
	int CornerNum=board_size.width*board_size.height;  // Number of corners in
	for (int ii=0 ; ii<total ;ii++)
	{
		if (0 == ii%CornerNum)    // Output Image Number 
		{	
			int i = -1;
			i = ii/CornerNum;
			int j=i+1;
			cout<<"--> The "<<j <<"th image --> : "<<endl;
		}
		if (0 == ii%3)	
		{
			cout<<endl;
		}
		else
		{
			cout.width(10);
		}
		//Output all Corners
		cout<<" -->"<<image_points_seq[ii][0].x;
		cout<<" -->"<<image_points_seq[ii][0].y;
	}	
	cout<<endl;
	cout<<"Corners Extracted...\n";

	// Calibration
	cout<<"Start Calibration...";
	// Real World Information of Chessboard
	Size square_size = Size(27,27);                    // The real size of one block on Chessboard
	vector<vector<Point3f> > object_points;            // xyz of corners
	// Cam param
	Mat cameraMatrix=Mat(3,3,CV_32FC1,Scalar::all(0)); // Camera Matrix
	vector<int> point_counts;  						   // NUmber of Corners in each Image
	Mat distCoeffs=Mat(1,5,CV_32FC1,Scalar::all(0));   // Distortion coefficients = (k1k2p1p2k3)
	vector<Mat> tvecsMat;                              // Translation vectors
	vector<Mat> rvecsMat;                              // Rotate vectors
	// Initialize
	int i,j,t;
	for (t=0;t<image_count;t++) 
	{
		vector<Point3f> tempPointSet;
		for (i=0;i<board_size.height;i++) 
		{
			for (j=0;j<board_size.width;j++) 
			{
				Point3f realPoint;
				// Chessborad  on the x-y platform
				realPoint.x = i*square_size.width;
				realPoint.y = j*square_size.height;
				realPoint.z = 0;
				tempPointSet.push_back(realPoint);
			}
		}
		object_points.push_back(tempPointSet);
	}
	// Initialize the number of corners, suppose all corners can be seen in the image
	for (i=0;i<image_count;i++)
	{
		point_counts.push_back(board_size.width*board_size.height);
	}	
	// Start Calibration
	calibrateCamera(object_points,image_points_seq,image_size,cameraMatrix,distCoeffs,rvecsMat,tvecsMat,0);
	cout<<"Finish!\n";
	// Assessment
	cout<<"Assessing...\n";
	double total_err = 0.0; 
	double err = 0.0; 
	vector<Point2f> image_points2;
	cout<<"Calibration Error :\n";
	fout<<"Calibration Error :\n";
	for (i=0;i<image_count;i++)
	{
		vector<Point3f> tempPointSet=object_points[i];
		// Use Param to calculate the new positions
		projectPoints(tempPointSet,rvecsMat[i],tvecsMat[i],cameraMatrix,distCoeffs,image_points2);
		// Calculate error between new and old positions
		vector<Point2f> tempImagePoint = image_points_seq[i];
		Mat tempImagePointMat = Mat(1,tempImagePoint.size(),CV_32FC2);
		Mat image_points2Mat = Mat(1,image_points2.size(), CV_32FC2);
		for (int j = 0 ; j < tempImagePoint.size(); j++)
		{
			image_points2Mat.at<Vec2f>(0,j) = Vec2f(image_points2[j].x, image_points2[j].y);
			tempImagePointMat.at<Vec2f>(0,j) = Vec2f(tempImagePoint[j].x, tempImagePoint[j].y);
		}
		err = norm(image_points2Mat, tempImagePointMat, NORM_L2);
		total_err += err/=  point_counts[i];   
		std::cout<<"The "<<i+1<<"th Mean Error :"<<err<<"pixels"<<endl;   
		fout<<"The "<<i+1<<"th Mean Error :"<<err<<"pixels"<<endl;   
	}   
	std::cout<<"Totoal Mean Error :"<<total_err/image_count<<"pixels"<<endl;   
	fout<<"Total Mean Error :"<<total_err/image_count<<"pixels"<<endl<<endl;   
	std::cout<<"Finish Assessment!"<<endl;  
	// Output to the file 	
	std::cout<<"Saving..."<<endl;       
	Mat rotation_matrix = Mat(3,3,CV_32FC1, Scalar::all(0)); 
	fout<<"Camera Matrix :"<<endl;   
	fout<<cameraMatrix<<endl<<endl;   
	fout<<"Distortion Coefficients\n";   
	fout<<distCoeffs<<endl<<endl<<endl;   
	for (int i=0; i<image_count; i++) 
	{ 
		fout<<"The "<<i+1<<"th Rotation vectors"<<endl;   
		fout<<rvecsMat[i]<<endl;   
  
		Rodrigues(rvecsMat[i],rotation_matrix);   
		fout<<"The "<<i+1<<"th Rotation Matrix"<<endl;   
		fout<<rotation_matrix<<endl;   
		fout<<"The "<<i+1<<"th Translation vectors"<<endl;   
		fout<<tvecsMat[i]<<endl<<endl;   
	}   
	std::cout<<"Finish Saving Distortion Coefficients..."<<endl; 
	fout<<endl;
	///////////////////////////////////////////////////////////////////////// 
    // Output undistorted Image         
    /////////////////////////////////////////////////////////////////////////
 	Mat mapx = Mat(image_size,CV_32FC1);
 	Mat mapy = Mat(image_size,CV_32FC1);
 	Mat R = Mat::eye(3,3,CV_32F);
 	std::cout<<"Save undistorted images..."<<endl;
 	string imageFileName;
 	std::stringstream StrStm;
 	for (int i = 0 ; i != image_count ; i++)
 	{
 		std::cout<<"Frame #"<<i+1<<"..."<<endl;
		initUndistortRectifyMap(cameraMatrix,distCoeffs,R,cameraMatrix,image_size,CV_32FC1,mapx,mapy);		
 		StrStm.clear();
 		imageFileName.clear();
		string filePath="./test_image/chess";
 		StrStm<<i+1;
 		StrStm>>imageFileName;
		filePath+=imageFileName;
		filePath+=".jpg";
 		Mat imageSource = imread(filePath);
 		Mat newimage = imageSource.clone();
		undistort(imageSource,newimage,cameraMatrix,distCoeffs);
 		//remap(imageSource,newimage,mapx, mapy, INTER_LINEAR);
		imshow("Origin Image",imageSource);
		imshow("Undistorted Image",newimage);
		waitKey();
 		StrStm.clear();
 		filePath.clear();
 		StrStm<<i+1;
 		StrStm>>imageFileName;
 		imageFileName += "_d.jpg";
 		imwrite(imageFileName,newimage);
 	}
 	std::cout<<"Finish Saving"<<endl;	
	return 0;
}