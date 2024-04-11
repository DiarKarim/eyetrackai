import cv2
import numpy as np
import pandas as pd
import serial

# Modify if your COM port is different
port = "COM4"
baudrate = 9600

# Your two numbers
number1 = 140
number2 = 150

# Setup video capture
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.025)
cap.set(cv2.CAP_PROP_SETTINGS, 1)

# Setup video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter("tmp/result.mp4", fourcc, fps, (int(width), int(height)))

circle_info = []

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
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2, 2)
    
    # Apply Hough Circle Transform
    circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=50, param2=30, minRadius=0, maxRadius=0)
    
    cv2.imwrite('test.png',frame)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            return [i[0], i[1], i[2]]
    return None

try:
    # Open the serial port
    with serial.Serial(port, baudrate, timeout=1) as ser:
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                circle = detect_circles(frame)
                if circle:
                    # Draw the circle in green and center in red
                    cv2.circle(frame, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
                    cv2.circle(frame, (circle[0], circle[1]), 2, (0, 0, 255), 5)
                    cv2.imshow('frame', frame)
                    cv2.waitKey(5)
                    circle_info.append(circle)

                    number1, number2 = circle[0], circle[1]

                    # Send data to serial port
                    data_string = f"{number1},{number2}\n"
                    ser.write(data_string.encode('ascii'))


                out.write(frame)
            else:
                break

except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")

# Cleanup
df = pd.DataFrame(circle_info, columns=['x', 'y', 'radius'])
df.to_csv("tmp/result.csv")
cap.release()
out.release()
cv2.destroyAllWindows()
