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
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Could not access camera")
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
                
                # Find faces in current frame using OpenCV
                face_cascade = cv2.CascadeClassifier('/home/runner/workspace/.pythonlibs/lib/python3.11/site-packages/cv2/data/haarcascade_frontalface_default.xml')
                gray_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_small_frame, 1.1, 4)
                face_locations = [(y, x+w, y+h, x) for (x, y, w, h) in faces]  # Convert to face_recognition format
                
                # Process each face found
                for (top, right, bottom, left) in face_locations:
                    # Scale back up face locations
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Extract face region for recognition
                    face_region = frame[top:bottom, left:right]
                    
                    # Try to match with known faces
                    name = self.face_utils.recognize_face(face_region)
                    
                    # Mark attendance if face is recognized
                    if name != "Unknown":
                        current_time = time.time()
                        # Prevent duplicate recognition within 5 seconds
                        if (name not in self.last_recognition_time or 
                            current_time - self.last_recognition_time[name] > 5):
                            
                            if name not in self.recognized_today:
                                success = self.attendance_manager.mark_attendance(name)
                                if success:
                                    self.recognized_today.add(name)
                                    print(f"Attendance marked for {name}")
                            
                            self.last_recognition_time[name] = current_time
                    
                    # Draw rectangle and label on frame
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), 
                               cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Encode frame for streaming
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                time.sleep(0.1)  # Limit frame rate
                
        except Exception as e:
            print(f"Camera error: {e}")
        finally:
            self.release_camera()

# Global attendance system instance
attendance_system = AttendanceSystem()

@app.route('/')
def index():
    """Main page with attendance tracking interface"""
    today_attendance = attendance_system.attendance_manager.get_today_attendance()
    enrolled_students = attendance_system.face_utils.get_enrolled_students()
    return render_template('index.html', 
                         attendance=today_attendance, 
                         enrolled_count=len(enrolled_students))

@app.route('/enroll')
def enroll_page():
    """Student enrollment page"""
    enrolled_students = attendance_system.face_utils.get_enrolled_students()
    return render_template('enroll.html', students=enrolled_students)

@app.route('/enroll_student', methods=['POST'])
def enroll_student():
    """Handle student enrollment with face capture"""
    try:
        student_name = request.form.get('student_name', '').strip()
        if not student_name:
            return jsonify({'success': False, 'message': 'Student name is required'})
        
        # Check if student already exists
        if student_name in attendance_system.face_utils.known_face_names:
            return jsonify({'success': False, 'message': 'Student already enrolled'})
        
        # Capture face from camera
        camera = attendance_system.get_camera()
        success, frame = camera.read()
        
        if not success:
            return jsonify({'success': False, 'message': 'Could not capture image from camera'})
        
        # Find face in captured frame using OpenCV
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier('/home/runner/workspace/.pythonlibs/lib/python3.11/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_frame, 1.1, 4)
        
        if len(faces) == 0:
            return jsonify({'success': False, 'message': 'No face detected in image'})
        
        if len(faces) > 1:
            return jsonify({'success': False, 'message': 'Multiple faces detected. Please ensure only one person is in frame'})
        
        # Get the first face region
        x, y, w, h = faces[0]
        face_region = frame[y:y+h, x:x+w]
        
        # Save student image
        student_image_path = f'student_images/{student_name}.jpg'
        cv2.imwrite(student_image_path, frame)
        
        # Add to known faces  
        attendance_system.face_utils.add_known_face(student_name, face_region)
        
        return jsonify({'success': True, 'message': f'Student {student_name} enrolled successfully'})
        
    except Exception as e:
        print(f"Enrollment error: {e}")
        return jsonify({'success': False, 'message': f'Enrollment failed: {str(e)}'})

@app.route('/video_feed')
def video_feed():
    """Video streaming route for live face recognition"""
    return Response(attendance_system.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_attendance')
def start_attendance():
    """Start attendance tracking"""
    try:
        # Reset daily recognition tracking
        attendance_system.recognized_today.clear()
        return jsonify({'success': True, 'message': 'Attendance tracking started'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/stop_attendance')
def stop_attendance():
    """Stop attendance tracking"""
    attendance_system.is_camera_active = False
    attendance_system.release_camera()
    return jsonify({'success': True, 'message': 'Attendance tracking stopped'})

@app.route('/get_attendance')
def get_attendance():
    """Get today's attendance data"""
    attendance_data = attendance_system.attendance_manager.get_today_attendance()
    return jsonify({'attendance': attendance_data})

@app.route('/delete_student/<student_name>')
def delete_student(student_name):
    """Delete enrolled student"""
    try:
        success = attendance_system.face_utils.delete_student(student_name)
        if success:
            return jsonify({'success': True, 'message': f'Student {student_name} deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Student not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("Starting Smart Attendance System...")
    print("Access the application at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
