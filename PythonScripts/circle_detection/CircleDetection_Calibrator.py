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

    def _detect_circles(self, grey, dp, minDist, param1, param2, minRadius, maxRadius):
        """
        Detects circles in a greyscale image using the Hough Circle Transform.

        :param gray: Grayscale image
        :return: Detected circles or None if no circles found
        """
        circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
                                    param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
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

    def process_frame(self, frame, dp, minDist, param1, param2, minRadius, maxRadius, threshold_distance=50):
        """
        Process a single frame to detect circles and compute the smoothed position.

        :param frame: The input frame to process.
        :param threshold_distance: Maximum distance between circles for smoothing
        :return: A tuple containing the smoothed position (x, y), and the frame with drawn circles, or (None, None) if no circles are detected.
        """
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grey = cv2.GaussianBlur(grey, (9, 9), 2)

        circles = self._detect_circles(grey, dp, minDist, param1, param2, minRadius, maxRadius)

        if circles is not None:
            avg_pos = np.mean(circles[0, :, :2], axis=0, dtype=np.float32)  # Use float32 for averaging
            self._update_positions(avg_pos, threshold_distance)

            # Take the smoothed position from the list of positions
            smoothed_pos = np.mean(self.circle_positions, axis=0, dtype=np.uint16)
            radius = circles[0, 0, 2]

            return smoothed_pos, self._draw_circle(frame, smoothed_pos, radius)

        return None, frame  # No circle detected


def nothing(x):
    pass

def main():
    cap = cv2.VideoCapture(0)  # Open the default camera
    detector = CircleDetector(num_frames=10)

    # Create a window to show the frames
    cv2.namedWindow('Circle Detection')

    # Create trackbars for Hough Circle parameters with minimum values > 0
    cv2.createTrackbar('dp', 'Circle Detection', 10, 20, nothing)  # dp in the range 1 to 2.0 (times 10)
    cv2.createTrackbar('minDist', 'Circle Detection', 1, 200, nothing)  # minDist should be > 0
    cv2.createTrackbar('param1', 'Circle Detection', 100, 300, nothing)  # param1 (Canny threshold) should be > 0
    cv2.createTrackbar('param2', 'Circle Detection', 30, 100, nothing)  # param2 threshold
    cv2.createTrackbar('minRadius', 'Circle Detection', 0, 100, nothing)
    cv2.createTrackbar('maxRadius', 'Circle Detection', 0, 200, nothing)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Get trackbar positions (adjust parameters during runtime)
        dp = max(cv2.getTrackbarPos('dp', 'Circle Detection') / 10.0, 1)  # Ensure dp >= 1
        minDist = max(cv2.getTrackbarPos('minDist', 'Circle Detection'), 1)  # Ensure minDist > 0
        param1 = max(cv2.getTrackbarPos('param1', 'Circle Detection'), 1)  # Ensure param1 > 0
        param2 = cv2.getTrackbarPos('param2', 'Circle Detection')
        minRadius = cv2.getTrackbarPos('minRadius', 'Circle Detection')
        maxRadius = cv2.getTrackbarPos('maxRadius', 'Circle Detection')
        

        # Process the frame with updated Hough Circle parameters
        coordinates, processed_frame = detector.process_frame(frame, dp, minDist, param1, param2, minRadius, maxRadius)

        if coordinates is not None:
            print(f"Detected Circle at: {coordinates}")

        # Show the processed frame
        cv2.imshow('Circle Detection', processed_frame)

        # Press 'q' to quit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()