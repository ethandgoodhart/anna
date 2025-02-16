import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
from collections import deque

# Initialize MediaPipe Hands with lower confidence thresholds
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Store previous hand position and gesture state
prev_x, prev_y = None, None
gesture_start_time = None
GESTURE_THRESHOLD_TIME = 0.08  # Even faster response
MOVEMENT_THRESHOLD = 0.06    # More sensitive
CONFIRMATION_FRAMES = 3    # Require fewer frames
PINCH_THRESHOLD = 0.05    # Threshold for pinch detection
gesture_count = 0

# Initialize movement tracking
current_gesture = None
performed_gestures = deque(maxlen=5)
is_pinched = False
prev_pinch_state = False

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to capture frame")
        continue

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with MediaPipe
    result = hands.process(rgb_frame)

    # Draw status on frame
    cv2.putText(frame, f"Current Gesture: {current_gesture}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Gesture Count: {gesture_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display last 5 performed gestures
    y_offset = 100
    cv2.putText(frame, "Last Performed Gestures:", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    for i, (gesture, timestamp) in enumerate(performed_gestures):
        elapsed = int(time.time() - timestamp)
        cv2.putText(frame, f"{gesture} ({elapsed}s ago)", (10, y_offset + 30 * (i + 1)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get thumb and index finger landmarks
            thumb_tip = hand_landmarks.landmark[4]  # Thumb tip
            index_finger = hand_landmarks.landmark[8]  # Index finger tip
            
            # Calculate pinch
            pinch_distance = np.sqrt(
                (thumb_tip.x - index_finger.x)**2 + 
                (thumb_tip.y - index_finger.y)**2
            )
            
            # Draw pinch distance
            thumb_x = int(thumb_tip.x * frame_width)
            thumb_y = int(thumb_tip.y * frame_height)
            finger_x = int(index_finger.x * frame_width)
            finger_y = int(index_finger.y * frame_height)
            
            # Draw thumb and index positions
            cv2.circle(frame, (thumb_x, thumb_y), 8, (0, 255, 0), -1)
            cv2.circle(frame, (finger_x, finger_y), 8, (0, 255, 0), -1)
            
            # Draw line between thumb and index
            cv2.line(frame, (thumb_x, thumb_y), (finger_x, finger_y), (255, 0, 0), 2)
            
            # Display pinch distance for debugging
            cv2.putText(frame, f"Pinch: {pinch_distance:.3f}", (10, frame_height - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Detect pinch gesture
            is_pinched = pinch_distance < PINCH_THRESHOLD
            
            # Detect pinch state change
            if is_pinched and not prev_pinch_state:
                print("\n=== GESTURE PERFORMED: PINCH ===")
                performed_gestures.appendleft(("Pinch", time.time()))
                pyautogui.press("space")  # You can change this to any key you want
            
            prev_pinch_state = is_pinched

            # Regular movement detection
            if prev_x is not None and prev_y is not None:
                dx = index_finger.x - prev_x
                dy = index_finger.y - prev_y

                # Draw movement vector
                cv2.line(frame, 
                        (int(prev_x * frame_width), int(prev_y * frame_height)),
                        (finger_x, finger_y),
                        (255, 0, 0), 2)

                # Display movement values for debugging
                cv2.putText(frame, f"dx: {dx:.3f}, dy: {dy:.3f}", (10, frame_height - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                if gesture_start_time is None:
                    gesture_start_time = time.time()
                elif time.time() - gesture_start_time > GESTURE_THRESHOLD_TIME:
                    if abs(dx) > abs(dy):  # Horizontal movement
                        if dx > MOVEMENT_THRESHOLD:
                            current_gesture = "Right"
                            gesture_count += 1
                            if gesture_count >= CONFIRMATION_FRAMES:
                                pyautogui.press("right")
                                print("\n=== GESTURE PERFORMED: WAVE RIGHT ===")
                                performed_gestures.appendleft(("Wave Right", time.time()))
                                gesture_count = 0
                                gesture_start_time = None
                        elif dx < -MOVEMENT_THRESHOLD:
                            current_gesture = "Left"
                            gesture_count += 1
                            if gesture_count >= CONFIRMATION_FRAMES:
                                pyautogui.press("left")
                                print("\n=== GESTURE PERFORMED: WAVE LEFT ===")
                                performed_gestures.appendleft(("Wave Left", time.time()))
                                gesture_count = 0
                                gesture_start_time = None
                    else:  # Vertical movement
                        if dy > MOVEMENT_THRESHOLD:
                            current_gesture = "Down"
                            gesture_count += 1
                            if gesture_count >= CONFIRMATION_FRAMES:
                                pyautogui.press("down")
                                print("\n=== GESTURE PERFORMED: WAVE DOWN ===")
                                performed_gestures.appendleft(("Wave Down", time.time()))
                                gesture_count = 0
                                gesture_start_time = None
                        elif dy < -MOVEMENT_THRESHOLD:
                            current_gesture = "Up"
                            gesture_count += 1
                            if gesture_count >= CONFIRMATION_FRAMES:
                                pyautogui.press("up")
                                print("\n=== GESTURE PERFORMED: WAVE UP ===")
                                performed_gestures.appendleft(("Wave Up", time.time()))
                                gesture_count = 0
                                gesture_start_time = None
                    
                    # Reset if no significant movement
                    if abs(dx) < MOVEMENT_THRESHOLD and abs(dy) < MOVEMENT_THRESHOLD:
                        gesture_count = 0
                        current_gesture = None

            prev_x, prev_y = index_finger.x, index_finger.y
    else:
        # Reset when no hand is detected
        prev_x, prev_y = None, None
        gesture_count = 0
        current_gesture = None
        gesture_start_time = None
        prev_pinch_state = False

    # Show the frame
    cv2.imshow("Hand Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()