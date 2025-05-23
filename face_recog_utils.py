# Real-time web feed
# anti-spoofing integrated
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime
import mediapipe as mp

path = 'student-faces'
images = []
names = []


for filename in os.listdir(path):
    img = cv2.imread(f'{path}/{filename}')
    images.append(img)
    names.append(os.path.splitext(filename)[0])

def find_encodings(images):
    encode_list = []
    for img in images:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(rgb)[0]
        encode_list.append(encode)
    return encode_list

known_encodings = find_encodings(images)

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

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            # Get coordinates for eye landmarks (left eye)
            LEFT_EYE = [33, 159, 145, 153, 154, 133]
            eye_coords = [(int(face_landmarks.landmark[i].x * frame.shape[1]),
                           int(face_landmarks.landmark[i].y * frame.shape[0])) for i in LEFT_EYE]

            # Compute Eye Aspect Ratio (simplified)
            def euclidean(p1, p2):
                return np.linalg.norm(np.array(p1) - np.array(p2))
            vert1 = euclidean(eye_coords[1], eye_coords[5])
            vert2 = euclidean(eye_coords[2], eye_coords[4])
            horz = euclidean(eye_coords[0], eye_coords[3])
            ear = (vert1 + vert2) / (2.0 * horz)
            print(f"EAR: {ear:.3f}")

            # Blink threshold: EAR below 0.25
            if ear < 0.6:
                print("ear found")
                for name in blink_counter:
                    blink_counter[name] += 1

            # Match face using face_recognition
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb_small)
            encodes = face_recognition.face_encodings(rgb_small, faces)

            for encode, face_loc in zip(encodes, faces):
                matches = face_recognition.compare_faces(known_encodings, encode)
                distance = face_recognition.face_distance(known_encodings, encode)
                best_match = np.argmin(distance)

                if matches[best_match]:
                    name = names[best_match].upper()
                    blink_counter.setdefault(name, 0)

                    # Only mark attendance after at least one blink
                    if blink_counter[name] >= 1:
                        y1, x2, y2, x1 = [val * 4 for val in face_loc]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, name + " ✅", (x1, y2 + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        mark_attendance(name)
                    else:
                        cv2.putText(frame, "BLINK TO VERIFY", (30, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame
