# This is to test camera feed
# This can work with spoofing 
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime

path = "student-faces"
images = []
names = []

for filename in os.listdir(path):
    img = cv2.imread(f"{path}/{filename}")
    images.append(img)
    names.append(os.path.splitext(filename)[0])

def find_encodings(images):
    encode_list = []
    for img in images:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img_rgb)[0]
        encode_list.append(encode)
    return encode_list

known_encodings = find_encodings(images)
print("Face encodings complete")

cap = cv2.VideoCapture(0)

def mark_attendance(name):
    with open("attendance.csv", "r+") as file:
        lines = file.readlines()
        logged_names = [line.split(",")[0] for line in lines]
        if name not in logged_names:
            now = datetime.now()
            time_string = now.strftime("%H:%M:%S")
            date_string = now.strftime("%Y-%m-%d")
            file.write(f"{name}, {date_string}, {time_string}\n")
            print(f"Attendance marked for {name}")

while True:
    success, frame = cap.read()

    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    faces_cur_frame = face_recognition.face_locations(rgb_frame)
    encodes_cur_frame = face_recognition.face_encodings(rgb_frame, faces_cur_frame)

    for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
        matches = face_recognition.compare_faces(known_encodings, encode_face)
        face_distances = face_recognition.face_distance(known_encodings, encode_face)
        match_index = np.argmin(face_distances)

        if matches[match_index]:
            name = names[match_index].upper()
            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            mark_attendance(name)

    cv2.imshow("Webcam Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()