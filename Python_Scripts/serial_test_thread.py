import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import serial
import random
import threading

# Modify if your COM port is different
port = "COM3"
baudrate = 115200

# Your two numbers
# number1 = 140
# number2 = 150

# servo_x_min = 140
# servo_x_max = 400
# servo_y_min = 280
# servo_y_max = 430

# img_width = 640
# img_height = 480
# mid_x = 270
# mid_y = 355
# cur_ser_x = mid_x
# cur_ser_y = mid_y

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.025)
cap.set(cv2.CAP_PROP_SETTINGS, 1)


class SerialThread(threading.Thread):
    def __init__(self, port, baudrate):
        super().__init__()
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.queue = []
        self.running = True

    def run(self):
        while self.running:
            if self.queue:
                data = self.queue.pop(0)
                self.serial_port.write(data.encode('ascii'))

    def send_data(self, data):
        self.queue.append(data)

    def stop(self):
        self.running = False
        self.serial_port.close()

# def map_value(circle):

def map_value(circle, servo_x_min, servo_y_min, servo_x_max, servo_y_max, img_width, img_height):
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

def main():
    serial_thread = SerialThread('COM3', 115200)
    serial_thread.start()

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
        
    try:
        # # Open the serial port
        # with serial.Serial(port, baudrate, timeout=1) as ser:
        #     data_string = f"{mid_x},{mid_y}\n"  # Add a newline as Arduino code expects it
        #     data_bytes = data_string.encode('ascii')
        
        print("Initiating...")
        # for i in range(5):
        #     ser.write(data_bytes)
        #     time.sleep(1)
        
        frameStartTime = 0.0
        previousTime = 0.0 

        # EMA Smoothing factor, tweak based on response speed vs. stability needs
        alpha = 0.01
        # Initialize EMA values to the middle positions
        ema_ser_x = mid_x
        ema_ser_y = mid_y
        loop_counter = 0 

        while (cap.isOpened()):
            
            frameStartTime = time.time()
            ret, frame = cap.read()
            if ret == True:
                circle, red = detect_circles(frame)
                # print(circle)
                result = frame.copy()
                cv2.imshow('origin', frame)
                cv2.waitKey(1)
                
                # cv2.imshow('red', red)
                # cv2.waitKey(5)
                if circle:
                    cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
                    # 绘制圆心
                    cv2.circle(result, (circle[0], circle[1]), 2, (0, 0, 255), 5)
                    cv2.imshow('frame', result)
                    cv2.waitKey(1)
                    
                    img_x = circle[0]
                    img_y = circle[1]
                    ser_x, ser_y = map_value((img_x, img_y),servo_x_min, servo_y_min, servo_x_max, servo_y_max, img_width, img_height)
                    ser_diff_x = ser_x - mid_x
                    ser_diff_y = ser_y - mid_y
                    new_ser_x = max(min(cur_ser_x + ser_diff_x, servo_x_max), 0)
                    new_ser_y = max(min(cur_ser_y + ser_diff_y, servo_y_max), 0)

                    # Update EMA values
                    ema_ser_x = alpha * new_ser_x + (1 - alpha) * ema_ser_x
                    ema_ser_y = alpha * new_ser_y + (1 - alpha) * ema_ser_y

                    # Create the data string
                    data_string = f"{ema_ser_x},{ema_ser_y}\n"  # Add a newline as Arduino code expects it
                    
                    # Send the data
                    serial_thread.send_data(data_string)

                    time.sleep(0.1)
                    cur_ser_x = new_ser_x
                    cur_ser_y = new_ser_y

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        cap.release()
                        serial_thread.stop()
                        break

                    fps = 1/(frameStartTime - previousTime)
                    print("FPS: " + str(np.round(fps)))
                    previousTime = frameStartTime

                    print(loop_counter)
                    loop_counter = loop_counter + 1

                # time.sleep(1)
        #         # out.write(result)
        #     else:
        #         break
        cap.release()
        serial_thread.stop()

    except serial.SerialException as e:
        print("Error: Could not open serial port:", e)


if __name__ == '__main__':
    main()