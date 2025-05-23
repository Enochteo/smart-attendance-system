# Smart Attendance System
An AI-powered attendance system that uses real-time face recognition and EAR liveness detection for lecturers or whoever to mark attendance through a web interface.

## Features
- Real-time face detection
- Blink-based liveness check (EAR to prevent spoofing)
- Web interface made with Flask
- Daily attendance logs in csv format
- Admin dashboard with attendance download
- Live camera preview to align your camera

## Tech Stack
- Python 3.10 (face recognition was not working with 3.11 apparently)
- Flask
- Open CV
- face_recognition
- MediaPipe
- Bootstrap

## Try it out...?
### 1. Clone
```bash
git clone https://github.com/Enochteo/smart-attendance-system.git
cd smart-attendance-system
```
### 2. Set up a virtual env
```bash
python -m venv venv
source venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txtx
```
### 4. Create your stored images directory
Name it "student-faces"
To use your own faces:
Place JPG images in the `students_faces/` folder.
The filename will be used as the name label.

### 5. Run
```bash
python app.py
```
Then visit http://127.0.0.1:5000


## Author
- **Enoch Owoade**
- email: enochowoade@gmail.com