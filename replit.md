# Smart Attendance System

## Overview

A web-based face recognition attendance system built with Flask that automatically tracks student attendance using computer vision. The system captures faces via webcam, matches them against enrolled students using facial recognition algorithms, and maintains attendance records in CSV format. Features include real-time video streaming, student enrollment interface, and daily attendance tracking with duplicate prevention.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Framework**: Flask with Jinja2 templating engine
- **UI Components**: Bootstrap 5 for responsive design with Font Awesome icons
- **Client-Side Logic**: Vanilla JavaScript for camera controls and real-time updates
- **Video Streaming**: Server-sent events for live camera feed display

### Backend Architecture
- **Application Structure**: Modular Flask application with separated concerns
  - `app.py`: Main Flask routes and application logic
  - `face_utils.py`: Face recognition and encoding management
  - `attendance_manager.py`: Attendance tracking and CSV operations
- **Class-Based Design**: Object-oriented approach with dedicated classes for each major component
- **Camera Management**: OpenCV integration for webcam access and video processing
- **Face Recognition**: Uses face_recognition library built on dlib for facial detection and encoding

### Data Storage Solutions
- **Attendance Records**: CSV files organized by date (`attendance_YYYY-MM-DD.csv`)
- **Face Encodings**: Pickle files for storing facial recognition data
- **Student Images**: File system storage in `student_images` directory
- **No Database**: Simple file-based approach for lightweight deployment

### Authentication and Authorization
- **No Authentication**: Open system design - all endpoints are publicly accessible
- **Session Management**: Not implemented - system relies on daily attendance tracking

### Core Features
- **Duplicate Prevention**: Tracks daily attendance to prevent multiple check-ins
- **Real-time Recognition**: Continuous face detection during active camera sessions
- **Student Enrollment**: Web interface for registering new students with face capture
- **Attendance Reporting**: Daily CSV generation with timestamp tracking

## External Dependencies

### Core Libraries
- **Flask**: Web framework for HTTP routing and templating
- **OpenCV (cv2)**: Computer vision library for camera operations and image processing
- **face_recognition**: Facial recognition library for encoding and matching faces
- **NumPy**: Numerical computing for array operations and image data manipulation
- **Pandas**: Data manipulation for CSV file operations and attendance reporting

### Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN for responsive UI components
- **Font Awesome 6**: Icon library via CDN for UI iconography

### Python Standard Library
- **pickle**: Serialization for face encoding persistence
- **csv**: CSV file operations for attendance records
- **datetime**: Timestamp generation and date formatting
- **threading**: Background processing for camera operations
- **os**: File system operations and directory management

### Hardware Requirements
- **Webcam**: Required for face capture and recognition functionality
- **File System**: Local storage for images, encodings, and attendance records