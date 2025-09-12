import os, cv2

local_cascade = os.path.join("data", "haarcascade_frontalface_default.xml")
print("Looking for:", local_cascade)
print("Exists:", os.path.exists(local_cascade))

cascade = cv2.CascadeClassifier(local_cascade)
print("Cascade loaded?", not cascade.empty())

