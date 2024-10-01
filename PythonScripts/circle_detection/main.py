import cv2
from CircleDetector import CircleDetector
from UDPClient import UDPClient


CAMERA_INDEX = 0

# Not very familar with UDP protocol, might need changing!
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

def main():
    detector = CircleDetector()
    udp_client = UDPClient(UDP_IP, UDP_PORT)
    
    while True:
        ret, frame = cap.read()
    
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Call the Process Frame function in CircleDetector to find the frame
        coordinates, frame = detector.process_frame(frame)

        if coordinates is not None:
            print(f"Center Coordinates (x, y): {coordinates[0]}, {coordinates[1]}")

            # Send coordinates over UDP:
            udp_client.send_coordinates(coordinates)

        # Display frame
        cv2.imshow('Real-Time Display', frame)

        # Pressing Q in the Window will stop the capture and end the program
        if cv2.waitKey(1) == ord('q'):
                break


if __name__ == "__main__":

    cap = cv2.VideoCapture(CAMERA_INDEX)

    # Checks if the camera in the given index is opened
    if not cap.isOpened():
        raise ValueError(f"Camera in Index {CAMERA_INDEX} cannot be opened.")
    
    main()
    
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()