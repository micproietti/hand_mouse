import cv2
import time
import math
import tkinter as tk
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pynput.mouse import Controller, Button


# ---------------- CONFIG ----------------

MODEL_PATH = "hand_landmarker.task"
CAM_INDEX = 0

SMOOTHING = 0.25                        # 0 = no smoothing, 1 = max smoothing (slow)
MOVE_THRESHOLD = 1.0                    # minimum distance in pixels to move the cursor

THUMB_INDEX_CLICK_THRESHOLD = 0.05
INDEX_MIDDLE_CLICK_THRESHOLD = 0.05

THUMB_MIDDLE_ENGAGE = 0.06
THUMB_MIDDLE_RELEASE = 0.09

SEL_ENGAGE_FRAMES = 4
SEL_RELEASE_FRAMES = 3

CLICK_DEBOUNCE = 0.45

# ---------------- HELPERS ----------------

def get_screen_size():
    root = tk.Tk()
    root.withdraw()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.destroy()
    return w, h

def create_hand_landmarker():
    BaseOptions = python.BaseOptions
    HandLandmarker = vision.HandLandmarker
    HandLandmarkerOptions = vision.HandLandmarkerOptions
    RunningMode = vision.RunningMode

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    return HandLandmarker.create_from_options(options)

# ---------------- MAIN PROGRAM ----------------

def main():
    screen_w, screen_h = get_screen_size()

    mouse = Controller()
    prev_mouse_x, prev_mouse_y = mouse.position
    smooth_x, smooth_y = prev_mouse_x, prev_mouse_y
    last_click_time = 0

    selecting = False
    sel_engage_counter = 0
    sel_release_counter = 0

    landmarker = create_hand_landmarker()

    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    print("Gestures:")
    print("thumb + index  -> left click")
    print("index + middle -> right click")
    print("thumb + middle (hold) -> selection")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break
            
            # Flipping the frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp = int(time.time() * 1000)

            result = landmarker.detect_for_video(mp_image, timestamp)

            if result.hand_landmarks:
                # Considering only first detected hand
                lm = result.hand_landmarks[0]

                # Relevant landmarks (thumb tip, index tip, middle finger tip); in the repo there is the picture of the hand with all the landmarks numbered
                thumb = lm[4]
                index = lm[8]
                middle = lm[12]

                # Extracting normalized coordinates
                tx, ty = thumb.x, thumb.y
                ix, iy = index.x, index.y
                mx, my = middle.x, middle.y

                # Convert normalized coords -> image pixels
                px_i = int(ix * frame.shape[1])
                py_i = int(iy * frame.shape[0])

                px_t = int(tx * frame.shape[1])
                py_t = int(ty * frame.shape[0])

                px_m = int(mx * frame.shape[1])
                py_m = int(my * frame.shape[0])

                # Drawing landmarks for debugging purpose (and it's cool imo)
                cv2.circle(frame, (px_i, py_i), 6, (0, 255, 0), -1)
                cv2.circle(frame, (px_t, py_t), 5, (0, 200, 200), -1)
                cv2.circle(frame, (px_m, py_m), 5, (255, 0, 0), -1)

                cv2.line(frame, (px_i, py_i), (px_t, py_t), (200, 200, 0), 1)
                cv2.line(frame, (px_i, py_i), (px_m, py_m), (200, 0, 200), 1)

                # Calculating distances
                d_ti = math.hypot(tx - ix, ty - iy)
                d_im = math.hypot(ix - mx, iy - my)
                d_tm = math.hypot(tx - mx, ty - my)

                # ---------------- CURSOR ----------------

                screen_x = ix * screen_w
                screen_y = iy * screen_h

                smooth_x = (1 - SMOOTHING) * smooth_x + SMOOTHING * screen_x
                smooth_y = (1 - SMOOTHING) * smooth_y + SMOOTHING * screen_y

                # Only move the cursor if the hand moved more than the threshold to avoid jitter
                if math.hypot(smooth_x - prev_mouse_x, smooth_y - prev_mouse_y) > MOVE_THRESHOLD:
                    mouse.position = (int(smooth_x), int(smooth_y))
                    prev_mouse_x, prev_mouse_y = smooth_x, smooth_y

                # ---------------- SELECTION ----------------

                if d_tm < THUMB_MIDDLE_ENGAGE:
                    sel_engage_counter += 1
                    sel_release_counter = 0
                else:
                    sel_engage_counter = 0
                    if d_tm > THUMB_MIDDLE_RELEASE:
                        sel_release_counter += 1
                    else:
                        sel_release_counter = 0

                if not selecting and sel_engage_counter >= SEL_ENGAGE_FRAMES:
                    mouse.press(Button.left)
                    selecting = True

                if selecting and sel_release_counter >= SEL_RELEASE_FRAMES:
                    mouse.release(Button.left)
                    selecting = False

                # ---------------- CLICKS ----------------

                now = time.time()

                if not selecting and d_ti < THUMB_INDEX_CLICK_THRESHOLD:
                    if now - last_click_time > CLICK_DEBOUNCE:
                        mouse.click(Button.left)
                        last_click_time = now

                if not selecting and d_im < INDEX_MIDDLE_CLICK_THRESHOLD:
                    if now - last_click_time > CLICK_DEBOUNCE:
                        mouse.click(Button.right)
                        last_click_time = now

                # ---------------- DEBUG DRAW ----------------

                cv2.putText(frame,
                            f"d_ti:{d_ti:.2f} d_im:{d_im:.2f} d_tm:{d_tm:.2f}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 255),
                            2)

            cv2.imshow("Hand Mouse", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        if selecting:
            mouse.release(Button.left)

        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()

if __name__ == "__main__":
    main()