"""
Smart Attendance System - Main Flask Application
Provides web interface for face recognition-based attendance tracking
"""

from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
import cv2
import numpy as np
import os
import pickle
from datetime import datetime
import threading
import time
from face_utils import FaceUtils
from attendance_manager import AttendanceManager

app = Flask(__name__)

class AttendanceSystem:
    def __init__(self):
        """Initialize the attendance system with required components"""
        self.face_utils = FaceUtils()
        self.attendance_manager = AttendanceManager()
        self.camera = None
        self.is_camera_active = False
        self.recognized_today = set()  # Track who has been marked present today
        self.last_recognition_time = {}  # Prevent rapid duplicate recognitions
        
        # Ensure required directories exist
        os.makedirs('student_images', exist_ok=True)
        os.makedirs('attendance_records', exist_ok=True)
        os.makedirs('face_encodings', exist_ok=True)
        
        # Load existing face encodings
        self.face_utils.load_encodings()
    
    def get_camera(self):
        """Initialize camera if not already active"""
        if self.camera is None:
            print("🔍 Scanning for available cameras...")
            for index in range(5):  # check first 5 indexes
                cam = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # force DirectShow backend
                if cam.isOpened():
                    print(f"✅ Camera opened successfully at index {index} (DirectShow)")
                    self.camera = cam
                    break
                else:
                    print(f"❌ Camera index {index} not available")
                cam.release()
            
            if self.camera is None:
                raise Exception("Could not access any camera")
        return self.camera

    def release_camera(self):
        """Release camera resources"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.is_camera_active = False
    
    def generate_frames(self):
        """Generate video frames with face recognition"""
        try:
            camera = self.get_camera()
            self.is_camera_active = True
            
            while self.is_camera_active:
                success, frame = camera.read()
                if not success:
                    break
                
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # ✅ Always use local Haar Cascade
                face_cascade = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
                gray_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_small_frame, 1.1, 4)
                face_locations = [(y, x+w, y+h, x) for (x, y, w, h) in faces]
                
                # Process each face found
                for (top, right, bottom, left) in face_locations:
                    # Scale back up
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    face_region = frame[top:bottom, left:right]
                    name = self.face_utils.recognize_face(face_region)
                    
                    if name != "Unknown":
                        current_time = time.time()
                        if (name not in self.last_recognition_time or 
                            current_time - self.last_recognition_time[name] > 5):
                            
                            if name not in self.recognized_today:
                                success = self.attendance_manager.mark_attendance(name)
                                if success:
                                    self.recognized_today.add(name)
                                    print(f"Attendance marked for {name}")
                            
                            self.last_recognition_time[name] = current_time
                    
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), 
                               cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Camera error: {e}")
        finally:
            self.release_camera()

# Global instance
attendance_system = AttendanceSystem()

@app.route('/')
def index():
    today_attendance = attendance_system.attendance_manager.get_today_attendance()
    enrolled_students = attendance_system.face_utils.get_enrolled_students()
    return render_template('index.html', 
                         attendance=today_attendance, 
                         enrolled_count=len(enrolled_students))

@app.route('/enroll')
def enroll_page():
    enrolled_students = attendance_system.face_utils.get_enrolled_students()
    return render_template('enroll.html', students=enrolled_students)

@app.route('/enroll_student', methods=['POST'])
def enroll_student():
    try:
        student_name = request.form.get('student_name', '').strip()
        if not student_name:
            return jsonify({'success': False, 'message': 'Student name is required'})
        
        if student_name in attendance_system.face_utils.known_face_names:
            return jsonify({'success': False, 'message': 'Student already enrolled'})
        
        camera = attendance_system.get_camera()
        success, frame = camera.read()
        
        if not success:
            return jsonify({'success': False, 'message': 'Could not capture image from camera'})
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ✅ Force load Haar Cascade with absolute path
        cascade_path = os.path.join(os.getcwd(), "data", "haarcascade_frontalface_default.xml")
        if not os.path.exists(cascade_path):
            cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")

        print("Loading Haar Cascade from:", cascade_path)
        face_cascade = cv2.CascadeClassifier(cascade_path)

        if face_cascade.empty():
            return jsonify({'success': False, 'message': f'Failed to load Haar cascade from {cascade_path}'})

        faces = face_cascade.detectMultiScale(gray_frame, 1.1, 4)
        
        if len(faces) == 0:
            return jsonify({'success': False, 'message': 'No face detected in image'})
        
        if len(faces) > 1:
            return jsonify({'success': False, 'message': 'Multiple faces detected. Please ensure only one person is in frame'})
        
        x, y, w, h = faces[0]
        face_region = frame[y:y+h, x:x+w]
        
        student_image_path = f'student_images/{student_name}.jpg'
        cv2.imwrite(student_image_path, frame)
        
        attendance_system.face_utils.add_known_face(student_name, face_region)
        
        return jsonify({'success': True, 'message': f'Student {student_name} enrolled successfully'})
        
    except Exception as e:
        print(f"Enrollment error: {e}")
        return jsonify({'success': False, 'message': f'Enrollment failed: {str(e)}'})



@app.route('/video_feed')
def video_feed():
    return Response(attendance_system.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_attendance')
def start_attendance():
    try:
        attendance_system.recognized_today.clear()
        return jsonify({'success': True, 'message': 'Attendance tracking started'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/stop_attendance')
def stop_attendance():
    attendance_system.is_camera_active = False
    attendance_system.release_camera()
    return jsonify({'success': True, 'message': 'Attendance tracking stopped'})

@app.route('/get_attendance')
def get_attendance():
    attendance_data = attendance_system.attendance_manager.get_today_attendance()
    return jsonify({'attendance': attendance_data})

@app.route('/delete_student/<student_name>')
def delete_student(student_name):
    try:
        success = attendance_system.face_utils.delete_student(student_name)
        if success:
            return jsonify({'success': True, 'message': f'Student {student_name} deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Student not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ✅ Favicon route (to silence browser 404)
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    print("Starting Smart Attendance System...")
    print("Access the application at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)


