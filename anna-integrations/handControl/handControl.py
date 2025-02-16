import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Store previous hand position
prev_x, prev_y = None, None
gesture_start_time = None
GESTURE_THRESHOLD_TIME = 0.2  # Time threshold to register a gesture
MOVEMENT_THRESHOLD = 0.1  # Movement threshold to detect significant gestures

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Mirror image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with MediaPipe
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the x, y coordinates of the wrist (landmark 0)
            wrist_x = hand_landmarks.landmark[0].x
            wrist_y = hand_landmarks.landmark[0].y

            if prev_x is not None and prev_y is not None:
                dx = wrist_x - prev_x
                dy = wrist_y - prev_y

                if gesture_start_time is None:
                    gesture_start_time = time.time()
                elif time.time() - gesture_start_time > GESTURE_THRESHOLD_TIME:
                    if abs(dx) > abs(dy):  # Horizontal movement
                        if dx > MOVEMENT_THRESHOLD:  # Right wave
                            pyautogui.press("right")
                            print("Wave Right")
                        elif dx < -MOVEMENT_THRESHOLD:  # Left wave
                            pyautogui.press("left")
                            print("Wave Left")
                    else:  # Vertical movement
                        if dy > MOVEMENT_THRESHOLD:  # Down wave
                            pyautogui.press("down")
                            print("Wave Down")
                        elif dy < -MOVEMENT_THRESHOLD:  # Up wave
                            pyautogui.press("up")
                            print("Wave Up")

                    gesture_start_time = None  # Reset gesture timer

            prev_x, prev_y = wrist_x, wrist_y

    cv2.imshow("Hand Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
