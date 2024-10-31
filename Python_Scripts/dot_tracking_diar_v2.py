import cv2
import numpy as np
import pandas as pd
import serial

# Modify if your COM port is different
port = "COM4"
baudrate = 9600

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.025)
cap.set(cv2.CAP_PROP_SETTINGS, 1)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Compute the center of the frame (camera view)
center_x = width // 2
center_y = height // 2

circle_info = []

def detect_circles(frame):
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

try:
    with serial.Serial(port, baudrate, timeout=1) as ser:
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                circle = detect_circles(frame)
                result = frame.copy()
                
                if circle:
                    # Draw the detected circle and its center
                    cv2.circle(result, (circle[0], circle[1]), circle[2], (0, 255, 0), 10)
                    cv2.circle(result, (circle[0], circle[1]), 2, (0, 0, 255), 5)
                    cv2.imshow('frame', result)
                    cv2.waitKey(5)
                    circle_info.append(circle)

                    # Compute the error/offset from the center
                    offset_x = circle[0] - center_x
                    offset_y = circle[1] - center_y

                    # Create the data string to send the offsets
                    data_string = f"{offset_x},{offset_y}\n"  # Format: "offset_x,offset_y\n"
                    data_bytes = data_string.encode('ascii')

                    # Send the data
                    ser.write(data_bytes)
                    print("Offsets sent successfully!")

                ser.write(result)
            else:
                break

except KeyboardInterrupt:
    print("User interrupted:", e)

df = pd.DataFrame(circle_info, columns=['x', 'y', 'radius'])
df.to_csv("tmp/result.csv")
cap.release()
