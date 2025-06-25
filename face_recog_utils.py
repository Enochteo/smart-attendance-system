# Real-time web feed
# anti-spoofing integrated
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime
import mediapipe as mp
from models import db, Student, AttendanceLog

path = 'student-faces'
images = []
names = []


for filename in os.listdir(path):
    img = cv2.imread(f'{path}/{filename}')
    images.append(img)
    names.append(os.path.splitext(filename)[0])

def load_known_faces(path="student-faces"):
    images, names, gnumbers = [], [], []

    for filename in os.listdir(path):
        img = cv2.imread(os.path.join(path, filename))
        if img is not None:
            images.append(img)

            # Extract gnumber and name from filename
            name_part = os.path.splitext(filename)[0]
            parts = name_part.split("-", 1)
            if len(parts) == 2:
                gnumber, name = parts
                gnumbers.append(gnumber)
                names.append(name.upper())
            else:
                print(f"[WARN] Filename '{filename}' not in 'G1234-Name.jpg' format.")

    encodings = []
    for img in images:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(rgb)
        if enc:
            encodings.append(enc[0])
        else:
            print(f"[WARN] Could not extract encoding from {filename}")

    return encodings, names, gnumbers

known_encodings, names, gnumbers = load_known_faces()

def mark_attendance(name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"attendance_{date_str}.csv"

    if not os.path.exists(filename):
        with open(filename, "w") as file:
            file.write("Name, Date, Time Entered\n")
    with open(filename, 'r+') as file:
        lines = file.readlines()
        if name not in [line.split(',')[0] for line in lines]:
            now = datetime.now()
            file.write(f'{name},{date_str},{now.strftime("%H:%M:%S")}\n')
        
            

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
blink_counter = {}

def detect_and_log_face(frame):
    global blink_counter
    name = None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            LEFT_EYE = [33, 159, 145, 153, 154, 133]
            eye_coords = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                           int(face_landmarks.landmark[i].y * frame.shape[0])) for i in LEFT_EYE]

            def euclidean(p1, p2):
                return np.linalg.norm(np.array(p1) - np.array(p2))
            vert1 = euclidean(eye_coords[1], eye_coords[5])
            vert2 = euclidean(eye_coords[2], eye_coords[4])
            horz = euclidean(eye_coords[0], eye_coords[3])
            ear = (vert1 + vert2) / (2.0 * horz)
            print(f"EAR: {ear:.3f}")

            if ear < 0.65:
                print("Blink detected")
                for name_key in blink_counter:
                    blink_counter[name_key] += 1

            # Face recognition
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb_small)
            encodes = face_recognition.face_encodings(rgb_small, faces)

            for encode, face_loc in zip(encodes, faces):
                matches = face_recognition.compare_faces(known_encodings, encode)
                distance = face_recognition.face_distance(known_encodings, encode)

                if distance is None or len(distance) == 0:
                    print("[WARN] No known face matches found — skipping frame.")
                    return frame, False

                best_match = np.argmin(distance)

                if matches[best_match]:
                    name = names[best_match].upper()
                    blink_counter.setdefault(name, 0)

                    if blink_counter[name] >= 1:
                        # Show visual feedback
                        y1, x2, y2, x1 = [val * 4 for val in face_loc]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, name + " ✅", (x1, y2 + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                        #  Save to AttendanceLog DB
                        matched_gnumber = gnumbers[best_match]
                        student = Student.query.filter_by(gnumber=matched_gnumber).first()
                        if student:
                            today = datetime.now()
                            print(today)
                            already_logged = AttendanceLog.query.filter(
                                AttendanceLog.student_id == student.id,
                                db.func.date(AttendanceLog.timestamp) == today
                            ).first()

                            if not already_logged:
                                log = AttendanceLog(student_id=student.id, status="Present")
                                db.session.add(log)
                                db.session.commit()
                                print(f"[INFO] Attendance marked for {name}")
                                marked_today.add(name)
                            else:
                                print(already_logged)

                    else:
                        cv2.putText(frame, "BLINK TO VERIFY", (30, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if name and name in blink_counter and blink_counter[name] >= 1:
        return frame, True
    else:
        return frame, False

