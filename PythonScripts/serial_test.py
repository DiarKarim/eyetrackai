import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import serial

# Modify if your COM port is different
port = "COM4"
baudrate = 9600

# Your two numbers
# number1 = 140
# number2 = 150


try:
    # Open the serial port
    with serial.Serial(port, baudrate, timeout=1) as ser:
        for x in range(14, 40):
            for y in range(28, 43):
                ser.write(f"{x*10},{y*10}\n".encode('ascii'))
                time.sleep(1)
        # while (cap.isOpened()):
        #     ret, frame = cap.read()
        #     if ret == True:
                # circle = detect_circles(frame)
                # print(circle)
                # result = frame.copy()
                #
                # if circle:
                    # cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
                    # # 绘制圆心
                    # cv2.circle(result, (circle[0], circle[1]), 2, (0, 0, 255), 5)
                    # cv2.imshow('frame', result)
                    # cv2.waitKey(5)
                    # circle_info.append(circle)
                    #
                    # number1 = circle[0]
                    # number2 = circle[1]
                    #
                    # # Create the data string
                    # data_string = f"{number1},{number2}\n"  # Add a newline as Arduino code expects it
                    # data_bytes = data_string.encode('ascii')
                    #
                    # # Send the data
                    # ser.write(data_bytes)
                    # print("Coordinates sent successfully!")

                # out.write(result)
            # else:
            #     break

except serial.SerialException as e:
    print("Error: Could not open serial port:", e)
