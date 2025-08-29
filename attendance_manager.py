"""
Attendance Management System
Handles attendance tracking, CSV file operations, and data management
"""

import csv
import os
from datetime import datetime
import pandas as pd

class AttendanceManager:
    def __init__(self):
        """Initialize attendance manager"""
        self.attendance_dir = 'attendance_records'
        os.makedirs(self.attendance_dir, exist_ok=True)
    
    def get_today_filename(self):
        """Get today's attendance filename"""
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.attendance_dir, f'attendance_{today}.csv')
    
    def mark_attendance(self, student_name):
        """
        Mark attendance for a student
        Returns True if successfully marked, False if already marked today
        """
        try:
            filename = self.get_today_filename()
            current_time = datetime.now()
            date_str = current_time.strftime('%Y-%m-%d')
            time_str = current_time.strftime('%H:%M:%S')
            
            # Check if student already marked present today
            if self.is_already_marked_today(student_name):
                print(f"{student_name} already marked present today")
                return False
            
            # Create CSV file with headers if it doesn't exist
            file_exists = os.path.exists(filename)
            
            with open(filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write headers if file is new
                if not file_exists:
                    writer.writerow(['Name', 'Date', 'Time'])
                
                # Write attendance record
                writer.writerow([student_name, date_str, time_str])
            
            print(f"Attendance marked for {student_name} at {time_str}")
            return True
            
        except Exception as e:
            print(f"Error marking attendance for {student_name}: {e}")
            return False
    
    def is_already_marked_today(self, student_name):
        """Check if student is already marked present today"""
        try:
            filename = self.get_today_filename()
            
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header row
                
                for row in reader:
                    if len(row) >= 1 and row[0] == student_name:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking attendance for {student_name}: {e}")
            return False
    
    def get_today_attendance(self):
        """Get today's attendance records"""
        try:
            filename = self.get_today_filename()
            
            if not os.path.exists(filename):
                return []
            
            attendance_records = []
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    attendance_records.append({
                        'name': row['Name'],
                        'date': row['Date'],
                        'time': row['Time']
                    })
            
            return attendance_records
            
        except Exception as e:
            print(f"Error getting today's attendance: {e}")
            return []
    
    def get_attendance_by_date(self, date_str):
        """Get attendance records for a specific date (YYYY-MM-DD format)"""
        try:
            filename = os.path.join(self.attendance_dir, f'attendance_{date_str}.csv')
            
            if not os.path.exists(filename):
                return []
            
            attendance_records = []
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    attendance_records.append({
                        'name': row['Name'],
                        'date': row['Date'],
                        'time': row['Time']
                    })
            
            return attendance_records
            
        except Exception as e:
            print(f"Error getting attendance for {date_str}: {e}")
            return []
    
    def get_student_attendance_history(self, student_name, days=30):
        """Get attendance history for a specific student"""
        try:
            history = []
            
            # Get all attendance files
            attendance_files = [f for f in os.listdir(self.attendance_dir) 
                              if f.startswith('attendance_') and f.endswith('.csv')]
            
            # Sort files by date (newest first)
            attendance_files.sort(reverse=True)
            
            # Limit to specified number of days
            if days > 0:
                attendance_files = attendance_files[:days]
            
            for filename in attendance_files:
                filepath = os.path.join(self.attendance_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Name'] == student_name:
                            history.append({
                                'name': row['Name'],
                                'date': row['Date'],
                                'time': row['Time']
                            })
            
            return history
            
        except Exception as e:
            print(f"Error getting attendance history for {student_name}: {e}")
            return []
    
    def get_attendance_statistics(self):
        """Get attendance statistics"""
        try:
            stats = {
                'total_days': 0,
                'total_attendances': 0,
                'unique_students': set(),
                'daily_counts': {}
            }
            
            # Get all attendance files
            attendance_files = [f for f in os.listdir(self.attendance_dir) 
                              if f.startswith('attendance_') and f.endswith('.csv')]
            
            stats['total_days'] = len(attendance_files)
            
            for filename in attendance_files:
                filepath = os.path.join(self.attendance_dir, filename)
                date = filename.replace('attendance_', '').replace('.csv', '')
                daily_count = 0
                
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        stats['total_attendances'] += 1
                        stats['unique_students'].add(row['Name'])
                        daily_count += 1
                
                stats['daily_counts'][date] = daily_count
            
            stats['unique_students'] = len(stats['unique_students'])
            
            return stats
            
        except Exception as e:
            print(f"Error getting attendance statistics: {e}")
            return {
                'total_days': 0,
                'total_attendances': 0,
                'unique_students': 0,
                'daily_counts': {}
            }
    
    def export_attendance_to_excel(self, start_date=None, end_date=None):
        """Export attendance data to Excel file"""
        try:
            # Get all attendance files
            attendance_files = [f for f in os.listdir(self.attendance_dir) 
                              if f.startswith('attendance_') and f.endswith('.csv')]
            
            all_records = []
            
            for filename in attendance_files:
                filepath = os.path.join(self.attendance_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        all_records.append({
                            'Name': row['Name'],
                            'Date': row['Date'],
                            'Time': row['Time']
                        })
            
            if all_records:
                df = pd.DataFrame(all_records)
                
                # Filter by date range if provided
                if start_date and end_date:
                    df['Date'] = pd.to_datetime(df['Date'])
                    start_date = pd.to_datetime(start_date)
                    end_date = pd.to_datetime(end_date)
                    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
                
                # Export to Excel
                excel_filename = f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                df.to_excel(excel_filename, index=False)
                print(f"Attendance data exported to {excel_filename}")
                return excel_filename
            else:
                print("No attendance data to export")
                return None
                
        except Exception as e:
            print(f"Error exporting attendance data: {e}")
            return None
