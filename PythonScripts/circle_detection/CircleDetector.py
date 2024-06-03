# Imports
import numpy as np
import cv2

class CircleDetector:
    def __init__(self, num_frames = 10):
        """
        Initialising the class with a given number of frames for smoothing.

        :param num_frames: Number of frames for moving average smoothing
        :param camera_index: Index of the Camera to use
        """

        self.num_frames = num_frames
        
        # This array contains positions of the circles that helps to smooth out the position as possible
        self.circle_positions = []


    def process_frame(self, frame, threshold_distance=50):
        """
        Process a single frame to detect circles and compute the smoothed position. The smoothing aspect considers how the detector seems 
            to track the same circle but each time this is called, the position seems to flicker around that spot.

        :param frame: The input frame to process.
        :param threshold_distance: Maximum distance between circles to localise smoothing effects 
        :return: A tuple containing the smoothed position (x, y), and Frame containing the drawing of the cirle, or (None, None) if no circles are detected.
        """
        
        # Convert the provided frame into grayscale and apply Gaussian Blurr to improve detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 2, 2)

        # Apply Hough Circle Transform to detect the circle in the frame
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=50, param2=30, minRadius=0, maxRadius=0)          

        if circles is not None:
            # Rounds the decimal of the position and radius of the circle
            circles = np.uint16(np.around(circles))

            # Using self.circle_positions, calculate the average circle position. This will help to smooth out the position of the current circle in a collection of a frame
            avg_pos = np.mean(circles[0,:, :2], axis=0, dtype=np.uint16)

            if len(self.circle_positions) > 0:
                # We check if the average position is significant to the last average position
                distance = np.linalg.norm(avg_pos - self.circle_positions[-1])
                if distance > threshold_distance:
                    self.circle_positions = [] # The list of circles resets if the distance between the new circle and last circle is greater (they're in different locations)

            # Add the new position to the list of cricles
            self.circle_positions.append(avg_pos)

            # Now, we need to smooth out the position of the circle as much as possible if the circle detected is stationary
            # Remove the oldest position every indicated frame in self.num_frames
            if len(self.circle_positions) > self.num_frames:
                self.circle_positions.pop(0)

            # Calculating the smoothed position of the circle
            smoothed_pos = np.mean(self.circle_positions, axis=0, dtype=np.uint16)
            radius = circles[0,0,2]

            # Draws the circle onto the frame
            if smoothed_pos is not None:
                # Draw the smoothed circle
                cv2.circle(frame, (smoothed_pos[0], smoothed_pos[1]), radius, (0, 255, 0), 2)
                # Draw the center of the circle
                cv2.circle(frame, (smoothed_pos[0], smoothed_pos[1]), 2, (0, 0, 255), 3)

            # Return the average position of the circle over the past frames and annotated frame
            return smoothed_pos, frame

        # If no circle detected, return None
        return None, frame
