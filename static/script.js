// Smart Attendance System JavaScript

class AttendanceSystem {
    constructor() {
        this.isRunning = false;
        this.attendanceInterval = null;
        this.initializeEventListeners();
        this.updateCurrentTime();
        this.startTimeUpdate();
    }

    initializeEventListeners() {
        // Start/Stop attendance buttons
        document.getElementById('start-btn').addEventListener('click', () => this.startAttendance());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopAttendance());
        
        // Refresh attendance button
        document.getElementById('refresh-attendance').addEventListener('click', () => this.refreshAttendance());
    }

    async startAttendance() {
        try {
            const startBtn = document.getElementById('start-btn');
            const stopBtn = document.getElementById('stop-btn');
            const cameraStatus = document.getElementById('camera-status');
            const videoFeed = document.getElementById('video-feed');
            const noCameraMsg = document.getElementById('no-camera-msg');

            // Disable start button and show loading
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';

            // Call start attendance endpoint
            const response = await fetch('/start_attendance');
            const data = await response.json();

            if (data.success) {
                this.isRunning = true;
                
                // Update UI
                startBtn.disabled = true;
                startBtn.innerHTML = '<i class="fas fa-play"></i> Start Attendance';
                stopBtn.disabled = false;
                
                // Update camera status
                cameraStatus.textContent = 'Camera Active';
                cameraStatus.className = 'badge bg-success';
                
                // Show video feed
                videoFeed.src = '/video_feed?' + new Date().getTime();
                videoFeed.style.display = 'block';
                noCameraMsg.style.display = 'none';
                
                // Start refreshing attendance data
                this.startAttendanceRefresh();
                
                this.showAlert('Success', 'Attendance tracking started successfully!', 'success');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error starting attendance:', error);
            this.showAlert('Error', 'Failed to start attendance tracking: ' + error.message, 'danger');
            
            // Reset button
            const startBtn = document.getElementById('start-btn');
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Attendance';
        }
    }

    async stopAttendance() {
        try {
            const startBtn = document.getElementById('start-btn');
            const stopBtn = document.getElementById('stop-btn');
            const cameraStatus = document.getElementById('camera-status');
            const videoFeed = document.getElementById('video-feed');
            const noCameraMsg = document.getElementById('no-camera-msg');

            // Call stop attendance endpoint
            const response = await fetch('/stop_attendance');
            const data = await response.json();

            if (data.success) {
                this.isRunning = false;
                
                // Update UI
                startBtn.disabled = false;
                stopBtn.disabled = true;
                
                // Update camera status
                cameraStatus.textContent = 'Camera Off';
                cameraStatus.className = 'badge bg-secondary';
                
                // Hide video feed
                videoFeed.style.display = 'none';
                videoFeed.src = '';
                noCameraMsg.style.display = 'block';
                
                // Stop refreshing attendance data
                this.stopAttendanceRefresh();
                
                this.showAlert('Info', 'Attendance tracking stopped.', 'info');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error stopping attendance:', error);
            this.showAlert('Error', 'Failed to stop attendance tracking: ' + error.message, 'danger');
        }
    }

    async refreshAttendance() {
        try {
            const refreshBtn = document.getElementById('refresh-attendance');
            const originalHtml = refreshBtn.innerHTML;
            
            // Show loading state
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            
            const response = await fetch('/get_attendance');
            const data = await response.json();
            
            this.updateAttendanceDisplay(data.attendance);
            
            // Reset button
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = originalHtml;
            
        } catch (error) {
            console.error('Error refreshing attendance:', error);
            this.showAlert('Error', 'Failed to refresh attendance data: ' + error.message, 'danger');
            
            // Reset button
            const refreshBtn = document.getElementById('refresh-attendance');
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        }
    }

    updateAttendanceDisplay(attendanceData) {
        const attendanceList = document.getElementById('attendance-list');
        const presentCount = document.getElementById('present-count');
        
        // Update count
        presentCount.textContent = attendanceData.length;
        
        if (attendanceData.length === 0) {
            attendanceList.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-clipboard-list fa-3x mb-3"></i>
                    <p>No attendance recorded today</p>
                </div>
            `;
        } else {
            attendanceList.innerHTML = attendanceData.map(record => `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                    <div>
                        <strong>${record.name}</strong>
                        <br><small class="text-muted">${record.time}</small>
                    </div>
                    <span class="badge bg-success">Present</span>
                </div>
            `).join('');
        }
    }

    startAttendanceRefresh() {
        // Refresh attendance data every 5 seconds
        this.attendanceInterval = setInterval(() => {
            if (this.isRunning) {
                this.refreshAttendance();
            }
        }, 5000);
    }

    stopAttendanceRefresh() {
        if (this.attendanceInterval) {
            clearInterval(this.attendanceInterval);
            this.attendanceInterval = null;
        }
    }

    updateCurrentTime() {
        const currentTimeElement = document.getElementById('current-time');
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        currentTimeElement.textContent = timeString;
    }

    startTimeUpdate() {
        // Update time every second
        setInterval(() => this.updateCurrentTime(), 1000);
    }

    showAlert(title, message, type = 'info') {
        const alertModal = document.getElementById('alertModal');
        const alertModalTitle = document.getElementById('alertModalTitle');
        const alertModalBody = document.getElementById('alertModalBody');
        
        alertModalTitle.textContent = title;
        alertModalBody.innerHTML = `
            <div class="alert alert-${type} mb-0">
                <i class="fas fa-${this.getIconForType(type)}"></i>
                ${message}
            </div>
        `;
        
        const modal = new bootstrap.Modal(alertModal);
        modal.show();
    }

    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize the attendance system when page loads
document.addEventListener('DOMContentLoaded', function() {
    const attendanceSystem = new AttendanceSystem();
    
    // Handle page visibility change to pause/resume video feed
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden, could pause video feed
            console.log('Page hidden');
        } else {
            // Page is visible again
            console.log('Page visible');
            if (attendanceSystem.isRunning) {
                // Refresh video feed
                const videoFeed = document.getElementById('video-feed');
                if (videoFeed.src) {
                    videoFeed.src = '/video_feed?' + new Date().getTime();
                }
            }
        }
    });
    
    // Handle errors in video feed
    document.getElementById('video-feed').addEventListener('error', function() {
        console.error('Video feed error');
        if (attendanceSystem.isRunning) {
            attendanceSystem.showAlert('Warning', 'Video feed interrupted. Please check camera connection.', 'warning');
        }
    });
});

// Utility functions for other parts of the application
window.AttendanceUtils = {
    formatTime: function(timeString) {
        // Format time string for display
        const time = new Date('1970-01-01T' + timeString + 'Z');
        return time.toLocaleTimeString('en-US', {
            hour12: true,
            hour: 'numeric',
            minute: '2-digit'
        });
    },
    
    formatDate: function(dateString) {
        // Format date string for display
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    downloadAttendance: function() {
        // Download attendance data as CSV (future feature)
        console.log('Download attendance feature coming soon...');
    }
};
