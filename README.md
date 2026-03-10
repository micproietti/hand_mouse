Hand-Controlled Mouse with MediaPipe

Simple project allows you to control your computer mouse using hand gestures captured from your webcam. It uses MediaPipe HandLandmarker for hand tracking and pynput to control the mouse.

Features

Move the mouse using your index finger.

Left click: thumb + index finger pinch.

Right click: index + middle finger pinch.

Text selection (hold): thumb + middle finger.

Real-time hand landmark visualization on your camera feed.

Smooth mouse movement with adjustable smoothing.# Hand-Controlled Mouse with MediaPipe

This project allows you to control your computer mouse using **hand gestures** captured from your webcam. It uses **MediaPipe HandLandmarker** for hand tracking and **pynput** to control the mouse.

---

## Features

- Move the mouse using your **index finger**.
- **Left click**: thumb + index finger pinch  
- **Right click**: index + middle finger pinch  
- **Text selection (hold)**: thumb + middle finger  
- Real-time hand landmark visualization on your camera feed  
- Smooth mouse movement with adjustable smoothing

---

## Requirements

- Python 3.12+  
- Webcam  

Install Python dependencies:

```bash
pip install opencv-python mediapipe pynput numpy

Requirements

Python 3.12+

Webcam

Install Python dependencies:

pip install opencv-python mediapipe pynput numpy

Important: Use Xorg if you are on Linux (Ubuntu 24 or similar).
The mouse movement with pynput may not work on Wayland, which is default in many modern Linux distributions.
To use Xorg, log out and choose "Ubuntu on Xorg" in the login screen.

Setup

Download the MediaPipe HandLandmarker model:

Save it as hand_landmarker.task in the same directory as hand_mouse.py.

You can get it from the MediaPipe Model Zoo
 or via the official Google repository.

Ensure your webcam is connected.

Run the program:

python hand_mouse.py
Controls

Index finger → move mouse

Thumb + index → left click

Index + middle → right click

Thumb + middle (hold) → select text

Press q to quit the program.

Notes

Adjust the smoothing, thresholds, and debounce values in hand_mouse.py if the cursor is jittery or too sensitive.

Keep your hand inside the webcam frame for best results.

Lighting affects detection quality; make sure the hand is well-lit.

License

This project is open-source and free to use for personal projects and experiments.