import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time 
import serial

ser = serial.Serial('COM8', 9600, timeout=1)
# cap = cv2.VideoCapture("tmp/test.mp4")
cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

midWidth = width // 2
midHeight = height // 2

fps = cap.get(cv2.CAP_PROP_FPS)

# Checking width and height for tuning the arduino code
print(f"width: {width}, height: {height}")
print(f"Mid Width: {midWidth}, Mid Height: {midHeight}")

out = cv2.VideoWriter("tmp/result.mp4", fourcc, fps, (int(width), int(height)))

circle_info = []


def detect_circles(frame):
    '''
    :param frame: input one frame
    :return: None or x,y coordinates and radius of circle center as a list
    '''
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2, 2)
    circles = cv2.HoughCircles(gray_blurred,
                               cv2.HOUGH_GRADIENT, 1, 50,
                               param1=50, param2=30, minRadius=0, maxRadius=0)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            return [i[0], i[1], i[2]]
    return None

def find_position(position):
    return [position[0]-midWidth, position[1]-midHeight]

# Resetting gaze position to 0,0
ser.write(('0,0'.encode()))


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        circle = detect_circles(frame)
        result = frame.copy()
        # print(circle)
        if circle:
            cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
            # 绘制圆心
            cv2.circle(result, (circle[0], circle[1]), 2, (0, 0, 255), 5)
            cv2.imshow('frame', result)
            cv2.waitKey(5)
            circle_info.append(circle)

            # Sending serial message to arduino
            pos = find_position(circle)
            print(pos)
            arduino_msg = ','.join(map(str, pos)) + '\n'
            ser.write(arduino_msg.encode())

        out.write(result)
    else:
        break

df = pd.DataFrame(circle_info, columns=['x', 'y', 'radius'])
df.to_csv("tmp/result.csv")
cap.release()
out.release()