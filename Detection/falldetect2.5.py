# Author Zeyu Chen
# Falling Detection System

import json
import os
import math
import smtplib
import time
import cv2 as cv
import numpy as np
import tkMessageBox
from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk

# Part1: Main
#
# Initializing

default_email = "chenzy@gatech.edu"
data_path = "sub_bg1"              # The default video path
valid_count = 0                    # The Frame Counter
old_valid_count = 0

# Initializing position information
average = 0
x_old = y_old = 0
head_x_old = head_y_old = 0
x_old_speed = x_speed = 0
y_old_speed = y_speed = 0
head_x_old_speed = head_x_speed = 0
head_y_old_speed = head_y_speed = 0

# Initializing Software Setting
target_email = default_email
target_video = data_path
old_frame = -30
ip_camera = ""

# Read the distance mapping file
distance_list = np.loadtxt('distance.txt')
distance = 0

# Part 2: Function
#
# Email
def send_alert():
    global target_email
    sender = 'fallingdetection17@gmail.com'
    receiver = [target_email]

    message = """From: From Falling Detection <fallingdetection17@gmail.com>
    To: <czyapply@gmail.com>
    Subject: Fall Alert

    Accidental fall happens. Please help.
    """

    try:
        session = smtplib.SMTP('smtp.gmail.com:587')
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(sender,'czywrjzyj17')
        session.sendmail(sender,receiver,message)
        session.quit()
        print "Successfully sent email"
    except smtplib.SMTPException:
       print "Error: unable to send email"


# Do analysis
index = 1
enable = 1
def do_analysis():
    global index
    global video_canvas_img, img
    global x_old, y_old, x_old_speed, y_old_speed, x_speed, y_speed
    global head_x_old, head_y_old, head_x_old_speed, head_x_speed, head_y_old_speed, head_y_speed
    global enable
    global old_frame

    file = target_video + "/Data/" + target_video + "_" + str(index).zfill(12) + "_keypoints.json"               
    try:
        fh = open(file)
    except IOError:
        index = 0
        tkMessageBox.showinfo("Alert", "\nNo files to be analyzed.\n\nPlease reset and try again.")
    else:
        with open(file) as f:  
            if f == None:
                return
            data = json.load(f)
            x = [0]*18
            y = [0]*18
            head_count = 0
            if data['people']:
                for i in range(0, 18):
                    x[i] = data['people'][0]['pose_keypoints'][3*i]
                    y[i] = data['people'][0]['pose_keypoints'][3*i + 1]

            # Take neck to represent the body 
            x_now = x[1]
            y_now = y[1]
            # Also take head into consideration, first count valid key pints of head, then compute their mean position
            if x[0] :
                head_count = head_count + 1
            for i in range(0, 4):
                if x[i + 14]:
                    head_count = head_count + 1
            # Calculate head position 
            head_x_now = 0
            head_y_now = 0
            if head_count :
                head_x_now = (x[0] + x[14] + x[15] + x[16] + x[17])/ head_count
                head_y_now = (y[0] + y[14] + y[15] + y[16] + y[17])/ head_count

            # Calculate speed
            x_old_speed = x_speed
            y_old_speed = y_speed
            head_x_old_speed = head_x_speed
            head_y_old_speed = head_y_speed
            x_speed = x_now - x_old
            y_speed = y_now - y_old
            head_x_speed = head_x_now - head_x_old  
            head_y_speed = head_y_now - head_y_old  
            # old_speed = speed
            # speed = math.sqrt((x_now - x_old)*(x_now - x_old) + (y_now - y_old)*(y_now - y_old))
            x_average = (x_speed + x_old_speed)/2
            y_average = (y_speed + y_old_speed)/2
            head_x_average = (head_x_speed + head_x_old_speed)/2
            head_y_average = (head_y_speed + head_y_old_speed)/2
            
            print "Frame:" + str(index) + " x_speed: " + str(x_average)
            print "Frame:" + str(index) + " y_speed: " + str(y_average)
            print "Frame:" + str(index) + " headx_speed: " + str(head_x_average)
            print "Frame:" + str(index) + " heady_speed: " + str(head_y_average)
            print " "

            # Update the position
            x_old = x_now
            y_old = y_now
            head_x_old = head_x_now
            head_y_old = head_y_now

            # Update distance
            distance = Distance(x, y)
            # Fall judge
            Fall (x_average, y_average, head_x_average, head_y_average, index, distance)
            

        img = PhotoImage(file = target_video + "/Image/" + target_video + "_" + str(index).zfill(12) + "_rendered.png")
        img = img.subsample(1, 1) 
        video_canvas.itemconfig(video_canvas_img, image = img)      
        index = index + 1
        if enable == 1:
            next_job = video_canvas.after(1, do_analysis)

# Fall Judge
def Fall(x_speed, y_speed, head_x_speed, head_y_speed, frame, distance):
    global valid_count # Robust
    global old_valid_count
    global old_frame
    
    # A fall is detected when both head and body speed meets the requirement
    if y_speed > 5.5 and head_y_speed > 5.5: 
        valid_count = valid_count + 1

    # To avoid wrong detection, only 4 continued frames that meets the requirement are regarded as fall
    if old_valid_count == valid_count:
        valid_count = 0
    old_valid_count = valid_count
    if valid_count > 4 and index - old_frame > 30: # We do not want the system to detect the same fall once more
        print "Fall Detected at Frame" + str(index) + ", " + "The person falls at " + str(distance) + " inches."
        time.sleep(5)
        old_frame = index
        send_alert()
        valid_count = 0

# Distance
def Distance(x, y):
    global distance_list
    global distance
    global index

    # Estimate the diameter of the head
    h1 = math.sqrt((x[16] - x[17])*(x[16] - x[17]) + (y[16] - y[17])*(y[16] - y[17]))
    h2 = math.sqrt((x[14] - x[16])*(x[14] - x[16]) + (y[14] - y[16])*(y[14] - y[16]))
    h3 = math.sqrt((x[15] - x[17])*(x[15] - x[17]) + (y[15] - y[17])*(y[15] - y[17]))
    h4 = math.sqrt((x[15] - x[16])*(x[15] - x[16]) + (y[15] - y[16])*(y[15] - y[16]))
    h5 = math.sqrt((x[14] - x[17])*(x[14] - x[17]) + (y[14] - y[17])*(y[14] - y[17]))

    # If the point is zero which means it is invalid
    if x[14] == 0:
        h2 = h5 = 0
    if x[15] == 0:
        h3 = h4 = 0
    if x[16] == 0:
        h1 = h2 = h4 = 0
    if x[17] == 0:
        h1 = h3 = h5 = 0
    hmax = max(h1, h2, h3, h4, h5)

    # Calculate the distance
    if index == 1 or abs(distance - distance_list[int(round(hmax))]) < 50:
        distance = distance_list[int(round(hmax))]
    return distance

# Part 3: UI
#
def Reset():
    global index
    global old_frame
    old_frame = -30
    index = 1
    enable = 1
    do_analysis()
# Email Set
def Email_Set():
    global top
    global email_entry
    global email_entrywindow
    email_entrywindow = Toplevel(top)
    email_entrywindow.geometry("300x100")
    email_entrywindow.title("Set New Email Address")
    Label(email_entrywindow, text="Set New Email Address", font = "Helvetica 16").pack(side = 'top')
    email_entry = Entry(email_entrywindow)
    email_entry.pack()
    # Button
    email_EntryButtons = Frame(email_entrywindow) 
    email_EntryButtons.pack()
    ## Submit Button
    email_button_submit = Button(email_EntryButtons, text = 'Submit', width = 10, command = Change_email)
    email_button_submit.pack(side = 'left')

    ## Cancel
    email_button_cancel = Button(email_EntryButtons, text = 'Cancel', width = 10, command = email_entrywindow.destroy)
    email_button_cancel.pack(side = 'right')
def Change_email():
    global target_email
    global email_entry
    global email_entrywindow
    
    if email_entry.get() == "":
        tkMessageBox.showinfo("Warning", "The input is invalid!")
        email_entrywindow.destroy()
        return
    target_email = email_entry.get()
    print  target_email
    email_entrywindow.destroy()
# Video_set
def Video_Set():
    global top
    global video_entry
    global video_entrywindow
    video_entrywindow = Toplevel(top)
    video_entrywindow.geometry("300x100")
    video_entrywindow.title("Choose a video")
    Label(video_entrywindow, text="Input the directory of Video", font = "Helvetica 16").pack(side = 'top')
    video_entry = Entry(video_entrywindow)
    video_entry.pack()
    # Button
    video_EntryButtons = Frame(video_entrywindow) 
    video_EntryButtons.pack()
    ## Submit Button
    video_button_submit = Button(video_EntryButtons, text = 'Submit', font = "Helvetica", width = 10, command = Change_video)
    video_button_submit.pack(side = 'left')

    ## Cancel
    video_button_cancel = Button(video_EntryButtons, text = 'Cancel', width = 10, command = video_entrywindow.destroy)
    video_button_cancel.pack(side = 'right')
def Change_video():
    global target_video
    global video_entry
    global video_entrywindow
    global old_frame
    old_frame = -30
    
    if video_entry.get() == "":
        tkMessageBox.showinfo("Warning", "The input is invalid!")
        video_entrywindow.destroy()
        return
    file = video_entry.get() + "/Data/" + video_entry.get() + "_" + str(index).zfill(12) + "_keypoints.json"  
    try:
        fh = open(file)
    except IOError:
        print "No such file!"
        tkMessageBox.showinfo("Warning", "\nDirectory not found!")  
        return  
    target_video = video_entry.get()
    print  target_video
    video_entrywindow.destroy()
# IP Camera Set
def Ipcamera_Set():
    global top
    global ip_entry
    global ip_entrywindow
    ip_entrywindow = Toplevel(top)
    ip_entrywindow.geometry("300x100")
    ip_entrywindow.title("Set Ip Camera Address")
    Label(ip_entrywindow, text="Set Ip Camera Address", font = "Helvetica 16").pack(side = 'top')
    ip_entry = Entry(ip_entrywindow)
    ip_entry.pack()
    # Button
    ip_EntryButtons = Frame(ip_entrywindow) 
    ip_EntryButtons.pack()
    ## Submit Button
    ip_button_submit = Button(ip_EntryButtons, text = 'Submit', width = 10, command = Change_ip)
    ip_button_submit.pack(side = 'left')

    ## Cancel
    ip_button_cancel = Button(ip_EntryButtons, text = 'Cancel', width = 10, command = ip_entrywindow.destroy)
    ip_button_cancel.pack(side = 'right')
def Change_ip():
    global ip_camera
    global ip_entry
    global ip_entrywindow
    
    if ip_entry.get() == "":
        tkMessageBox.showinfo("Warning", "The input is invalid!")
        ip_entrywindow.destroy()
        return
    ip_camera = ip_entry.get()
    print  ip_camera
    ip_entrywindow.destroy()

def Start():
    global enable
    global old_frame
    old_frame = -30
    enable = 1
    do_analysis()
def Help():
    global top
    global help_window
    help_window = Toplevel(top)
    help_window.geometry("300x200")
    help_window.title("Help")
    Label(help_window, text="Instructions", font = "Helvetica 16").pack(side = 'top')
    Label(help_window, text="Analyze, start in video mode.", font = "Helvetica 12").pack()
    Label(help_window, text="Pause, pause the process.", font = "Helvetica 12").pack()
    Label(help_window, text="One Frame, run one frame a one-click.", font = "Helvetica 12").pack()
    Label(help_window, text="Real Time, process the video stream, \nopenpose is required.", font = "Helvetica 12").pack()
def About():
    about_text = "\nFalling Detection ver2.5\n\nThis software is designed to detect unexpected fall and send alert by email.\n\nAuthor: Zeyu Chen"
    tkMessageBox.showinfo("About", about_text)
def Pause():
    global enable
    enable = 0
def One_Frame():
    global enable
    enable = 0
    do_analysis()
def Real_Time():
    global data_path
    global ip_camera
    global enable

    if ip_camera == "":
        tkMessageBox.showinfo("Warning", "\nPlease Set WebCam Address!")
        return

    data_path = "real_time"
    s = "rm -rf real_time"
    os.system(s)
    s = "./build/examples/openpose/openpose.bin --no_display --write_images real_time/Image/ --write_keypoint_json real_time/Data --net_resolution 640x480--ip_camera " + ip_camera
    os.system(s)
    # time.pause(10)
    enable = 1
    do_analysis()
# UI TOP
top = Tk()
top.geometry("800x550")
top.title("Falling Detection")
# Menu
menu = Menu(top)
top.config(menu = menu)

filemenu = Menu(menu)
filemenu.add_command(label = "Set Email Adress", command = Email_Set)
filemenu.add_command(label = "Set Test Video", command = Video_Set)
filemenu.add_command(label = "Set IP Camera", command = Ipcamera_Set)
filemenu.add_command(label = "Reset", command = Reset)
filemenu.add_separator()
filemenu.add_command(label = "Exit", command = top.quit)
menu.add_cascade(label = "File", menu = filemenu)

helpmenu = Menu(menu)
helpmenu.add_command(label = "Help", command = Help)
helpmenu.add_command(label = "About", command = About)
menu.add_cascade(label = "Help", menu = helpmenu)
# Title
title_label = Label(top, text = "Falling Detection ver2.5", font = "Helvetica 16 bold")   
title_label.pack(pady = 10) 

# Button
Buttons = Frame(top) 
Buttons.pack(side = 'left')
## Analyze Button
button_do = Button(Buttons, text = 'Analyze', width = 10, command = Start)
button_do.pack(pady = 10)

## Pause
button_Pause = Button(Buttons, text = 'Pause', width = 10, command = Pause)
button_Pause.pack(pady = 10)

## One Frame
button_Continue = Button(Buttons, text = 'One Frame', width = 10, command = One_Frame)
button_Continue.pack(pady = 10)

## Real Time
button_Real_Time = Button(Buttons, text = 'Real Time', width = 10, command = Real_Time)
button_Real_Time.pack(pady = 10)

# Video
Videos = Frame(top, width=500, height=500)
Videos.pack(side = 'right')
video_canvas = Canvas(Videos, width=700, height=400)
video_canvas.pack()
Frame0 = PhotoImage(file = "logo.png")
Frame0 = Frame0.subsample(1, 1) #640*480
video_canvas_img = video_canvas.create_image(300, 200, image=Frame0)


top.mainloop()

