import numpy as np
import cv2

class CircleDetector:
    def __init__(self, num_frames=1):
        """
        Initializing the class with a given number of frames for smoothing.
        
        :param num_frames: Number of frames for moving average smoothing
        """
        self.num_frames = num_frames
        self.circle_positions = []

    def process_frame(self, frame, dp, minDist, param1, param2, minRadius, maxRadius, threshold_distance=50):
        """
        Process a single frame to detect circles with the current Hough Circle parameters.
        
        :param frame: The input frame to process
        :param dp: Inverse ratio of the accumulator resolution to the image resolution
        :param minDist: Minimum distance between the centers of detected circles
        :param param1: Higher threshold for the Canny edge detector
        :param param2: Accumulator threshold for circle detection
        :param minRadius: Minimum radius of detected circles
        :param maxRadius: Maximum radius of detected circles
        :param threshold_distance: Maximum distance between circles to localize smoothing effects
        :return: A tuple containing the smoothed position (x, y), and the frame with the circle drawn, or (None, None) if no circles are detected
        """
        
        # Convert the frame to grayscale and apply GaussianBlur to reduce noise
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 2, 2)

        # Apply Hough Circle Transform with the trackbar values
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp, minDist,
            param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))

            # Calculate the average position of detected circles
            avg_pos = np.mean(circles[0, :, :2], axis=0, dtype=np.uint16)

            if len(self.circle_positions) > 0:
                distance = np.linalg.norm(avg_pos - self.circle_positions[-1])
                if distance > threshold_distance:
                    self.circle_positions = []

            self.circle_positions.append(avg_pos)

            if len(self.circle_positions) > self.num_frames:
                self.circle_positions.pop(0)

            smoothed_pos = np.mean(self.circle_positions, axis=0, dtype=np.uint16)
            radius = circles[0, 0, 2]

            # Draw the circle on the frame
            cv2.circle(frame, (smoothed_pos[0], smoothed_pos[1]), radius, (0, 255, 0), 2)
            cv2.circle(frame, (smoothed_pos[0], smoothed_pos[1]), 2, (0, 0, 255), 3)

            return smoothed_pos, frame

        return None, frame

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
