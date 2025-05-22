import cv2
import serial
import time

# === Config ===
PORT = "COM11"
BAUD = 9600
CAMERA_INDEX = 0

# Servo range limits
Y_MIN, Y_MAX = 100, 200
X_MIN, X_MAX = 100, 300

Y_MID = 150
X_MID = 200

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

current_x = X_MID
current_y = Y_MID

def send_servo_values(y, x):
    global current_x, current_y
    try:
        with serial.Serial(PORT, BAUD, timeout=1) as arduino:
            time.sleep(2)
            command = f"{y},{x}\n"
            arduino.write(command.encode())
            print(f"Sent: {command.strip()}")
            current_y, current_x = y, x
    except Exception as e:
        print("Serial Error:", e)

def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        dx = x - FRAME_WIDTH // 2
        dy = y - FRAME_HEIGHT // 2

        sensitivity = 0.1
        move_x = int(current_x - dx * sensitivity)
        move_y = int(current_y - dy * sensitivity)

        move_x = max(X_MIN, min(X_MAX, move_x))
        move_y = max(Y_MIN, min(Y_MAX, move_y))

        print(f"Click at ({x}, {y}) -> Moving to Y: {move_y}, X: {move_x}")
        send_servo_values(move_y, move_x)

def track_target(cap):
    print("Select object to track...")
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera.")
        return

    bbox = cv2.selectROI("Tracking", frame, fromCenter=False)
    tracker = cv2.TrackerCSRT_create()
    ok = tracker.init(frame, bbox)

    sensitivity = 0.1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ok, bbox = tracker.update(frame)
        if ok:
            x, y, w, h = [int(v) for v in bbox]
            cx = x + w // 2
            cy = y + h // 2
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

            dx = cx - FRAME_WIDTH // 2
            dy = cy - FRAME_HEIGHT // 2

            move_x = int(current_x - dx * sensitivity)
            move_y = int(current_y - dy * sensitivity)

            move_x = max(X_MIN, min(X_MAX, move_x))
            move_y = max(Y_MIN, min(Y_MAX, move_y))

            send_servo_values(move_y, move_x)

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) == 27:  # ESC to quit
            break

    cv2.destroyWindow("Tracking")

def main():
    global current_x, current_y

    mode = input("Choose mode ('click' or 'track'): ").strip().lower()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    send_servo_values(Y_MID, X_MID)

    time.sleep(2)

    if mode == "click":
        cv2.namedWindow("Click to Look")
        cv2.setMouseCallback("Click to Look", on_mouse_click)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.line(frame, (FRAME_WIDTH//2, 0), (FRAME_WIDTH//2, FRAME_HEIGHT), (0, 255, 0), 1)
            cv2.line(frame, (0, FRAME_HEIGHT//2), (FRAME_WIDTH, FRAME_HEIGHT//2), (0, 255, 0), 1)
            cv2.imshow("Click to Look", frame)

            if cv2.waitKey(1) == 27:
                break

        cv2.destroyWindow("Click to Look")

    elif mode == "track":
        track_target(cap)

    else:
        print("Invalid mode selected.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
