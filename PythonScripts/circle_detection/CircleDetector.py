import numpy as np
import cv2

class CircleDetector:
    def __init__(self, num_frames=10, smoothing_factor=1.0):
        """
        Initialises the class with a given number of frames for smoothing.

        :param num_frames: Number of frames for moving average smoothing
        :param smoothing_factor: Factor to weight the previous position
        """
        self.num_frames = num_frames
        self.smoothing_factor = smoothing_factor
        self.circle_positions = []

    def _detect_circles(self, gray):
        """
        Detects circles in a greyscale image using the Hough Circle Transform.

        :param gray: Grayscale image
        :return: Detected circles or None if no circles found
        """
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                                    param1=100, param2=50, minRadius=0, maxRadius=0)
        return np.uint16(np.around(circles)) if circles is not None else None

    def _update_positions(self, avg_pos, threshold_distance):
        """
        Updates the list of circle positions with a new average position.

        :param avg_pos: The average position of detected circles
        :param threshold_distance: Threshold distance for smoothing
        :return: None
        """
        if self.circle_positions:
            distance = np.linalg.norm(avg_pos - self.circle_positions[-1])
            if distance > threshold_distance:
                self.circle_positions.clear()  # Reset if the circle moved significantly

        # Use a weighted approach for smoothing
        if self.circle_positions:
            last_pos = self.circle_positions[-1]
            new_smoothed_pos = self.smoothing_factor * last_pos + (1 - self.smoothing_factor) * avg_pos
            self.circle_positions.append(new_smoothed_pos)
        else:
            self.circle_positions.append(avg_pos)  # First entry

        # Maintain the size of circle_positions
        if len(self.circle_positions) > self.num_frames:
            self.circle_positions.pop(0)

    def _draw_circle(self, frame, smoothed_pos, radius):
        """
        Draws the detected circle and its center on the frame.

        :param frame: The original frame
        :param smoothed_pos: Smoothed position of the detected circle
        :param radius: Radius of the detected circle
        :return: The annotated frame
        """
        cv2.circle(frame, (int(smoothed_pos[0]), int(smoothed_pos[1])), radius, (0, 255, 0), 2)
        cv2.circle(frame, (int(smoothed_pos[0]), int(smoothed_pos[1])), 2, (0, 0, 255), 3)
        return frame

    def process_frame(self, frame, threshold_distance=50):
        """
        Process a single frame to detect circles and compute the smoothed position.

        :param frame: The input frame to process.
        :param threshold_distance: Maximum distance between circles for smoothing
        :return: A tuple containing the smoothed position (x, y), and the frame with drawn circles, or (None, None) if no circles are detected.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = self._detect_circles(gray)

        if circles is not None:
            avg_pos = np.mean(circles[0, :, :2], axis=0, dtype=np.float32)  # Use float32 for averaging
            self._update_positions(avg_pos, threshold_distance)

            # Take the smoothed position from the list of positions
            smoothed_pos = np.mean(self.circle_positions, axis=0, dtype=np.uint16)
            radius = circles[0, 0, 2]

            return smoothed_pos, self._draw_circle(frame, smoothed_pos, radius)

        return None, frame  # No circle detected
