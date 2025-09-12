"""
Webcam Access Module
Provides functions to open and capture frames from webcam
"""

import cv2

def get_camera(index_range=5):
    """
    Try to open available cameras (0–4) with DirectShow backend.
    Returns an opened VideoCapture object or None if no camera works.
    """
    print("🔍 Scanning for available cameras...")
    for index in range(index_range):
        camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # force DirectShow backend
        if camera.isOpened():
            print(f"✅ Camera opened successfully at index {index} (DirectShow)")
            return camera
        else:
            print(f"❌ Camera index {index} not available")
        camera.release()
    return None


def capture_frame(camera):
    """
    Capture a single frame from an opened camera
    """
    if camera is None or not camera.isOpened():
        print("❌ Camera is not initialized")
        return None

    ret, frame = camera.read()
    if not ret:
        print("⚠️ Failed to capture frame")
        return None
    return frame
