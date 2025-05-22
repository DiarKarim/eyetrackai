import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import serial
import random

# Modify if your COM port is different
port = "COM4"
baudrate = 115200

# Your two numbers
# number1 = 140
# number2 = 150
servo_x_min = 140
servo_x_max = 400
servo_y_min = 280
servo_y_max = 430

img_width = 640
img_height = 480
mid_x = 270
mid_y = 355
cur_ser_x = mid_x
cur_ser_y = mid_y
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.025)
cap.set(cv2.CAP_PROP_SETTINGS, 1)

def map_value(circle):
    x = circle[0]
    y = circle[1]
    servo_x = servo_x_max - ((x - 0) / (img_width - 0)) * (servo_x_max - servo_x_min)
    servo_y = servo_y_max - ((y - 0) / (img_height - 0)) * (servo_y_max - servo_y_min)
    return int(servo_x), int(servo_y)

def detect_circles(frame):
    '''
    Detects red circles in a frame.
    :param frame: Input frame
    :return: None or x,y coordinates and radius of circle center as a list
    '''
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define range of red color in HSV
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    
    # Threshold the HSV image to get only red colors
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2
    
    # Bitwise-AND mask and original image
    red_only = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Convert to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(red_only, cv2.COLOR_BGR2GRAY)
    
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2, 2)
    
    # Apply Hough Circle Transform
    circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=50, param2=30, minRadius=0, maxRadius=0)
    
    # cv2.imwrite('test.png',frame)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            return [i[0], i[1], i[2]], red_only
    return None, red_only

try:
    # Open the serial port
    with serial.Serial(port, baudrate, timeout=1) as ser:
        data_string = f"{mid_x},{mid_y}\n"  # Add a newline as Arduino code expects it
        data_bytes = data_string.encode('ascii')
        
        print("Initiating...")
        for i in range(5):
            ser.write(data_bytes)
            time.sleep(1)
        # x_min, x_max = 140, 400
        # y_min, y_max = 280, 430
        # for i in range(100):
        #     random_x = random.randint(0, 640)
        #     random_y = random.randint(0, 480)
        #     ser_x, ser_y = map_value((random_x, random_y))
        # ser_x = servo_x_min
        # ser_y = servo_y_max
        # data_string = f"{ser_x},{ser_y}\n"  # Add a newline as Arduino code expects it
        # data_bytes = data_string.encode('ascii')
                
                # Send the data
        # ser.write(data_bytes)
        # print("img x:{},y:{}, servo x:{},y:{} Coordinates sent successfully!".format(random_x, random_y, ser_x, ser_y))
        # time.sleep(1)
        while (cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                circle, red = detect_circles(frame)
                # print(circle)
                result = frame.copy()
                cv2.imshow('origin', frame)
                cv2.waitKey(5)
                
                # cv2.imshow('red', red)
                # cv2.waitKey(5)
                if circle:
                    cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
                    # 绘制圆心
                    cv2.circle(result, (circle[0], circle[1]), 2, (0, 0, 255), 5)
                    cv2.imshow('frame', result)
                    cv2.waitKey(5)
                    # circle_info.append(circle)
                    
                    img_x = circle[0]
                    img_y = circle[1]
                    ser_x, ser_y = map_value((img_x, img_y))
                    ser_diff_x = ser_x - mid_x
                    ser_diff_y = ser_y - mid_y
                    new_ser_x = max(min(cur_ser_x + ser_diff_x, servo_x_max), 0)
                    new_ser_y = max(min(cur_ser_y + ser_diff_y, servo_y_max), 0)
                    # Create the data string
                    data_string = f"{new_ser_x},{new_ser_y}\n"  # Add a newline as Arduino code expects it
                    data_bytes = data_string.encode('ascii')
                    
                    # Send the data
                    ser.write(data_bytes)
                    print("img x:{},y:{}, cur_ser_x:{}, cur_ser_y:{}, ser_x:{}, ser_y:{}, new servo x:{},y:{} diff_x:{}, diff_y:{}".format(img_x, img_y, 
                                                                                                              cur_ser_x, cur_ser_y, ser_x, ser_y,
                                                                                       new_ser_x, new_ser_y, 
                                                                                       ser_diff_x, ser_diff_y))
                    time.sleep(0.5)
                    cur_ser_x = new_ser_x
                    cur_ser_y = new_ser_y

                # time.sleep(1)
        #         # out.write(result)
        #     else:
        #         break

except serial.SerialException as e:
    print("Error: Could not open serial port:", e)