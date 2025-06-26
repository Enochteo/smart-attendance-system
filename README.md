# Smart Attendance System
An AI-powered attendance system that uses real-time face recognition and EAR liveness detection for professors or whoever to mark attendance through a web interface.

## Features
- Real-time face detection
- Blink-based liveness check (EAR to prevent spoofing)
- Web interface made with Flask
- Daily attendance logs in csv format
- Admin dashboard with attendance download
- Live camera preview to align your camera

## Tech Stack
- Python 3.10 (face recognition does not working with 3.11)
- Flask
- Open CV
- face_recognition
- MediaPipe
- Bootstrap


## Demo
![Demo_vid](Smart_attendance_demo1.gif)

## Try it out...?
## Deployed website -> https://smart-attendance-system-production-0088.up.railway.app/
or try it out locally visit logs.md for details and also before visiting the website.

### To add:
- Authorization for admin
- Create cloud base for logs 
- Hardware integration: Add ESP32 and RFID marking system as well
## Author
- **Enoch Owoade**
- email: enochowoade@gmail.com
