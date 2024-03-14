import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time 
import serial

# cap = cv2.VideoCapture("tmp/test.mp4")
cap = cv2.VideoCapture(1)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

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


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        circle = detect_circles(frame)
        print(circle)
        result = frame.copy()
        
        if circle:
            cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
            # 绘制圆心
            cv2.circle(result, (circle[0], circle[1]), 2, (0, 0, 255), 5)
            cv2.imshow('frame', result)
            cv2.waitKey(5)
            circle_info.append(circle)
        out.write(result)
    else:
        break
df = pd.DataFrame(circle_info, columns=['x', 'y', 'radius'])
df.to_csv("tmp/result.csv")
cap.release()
out.release()