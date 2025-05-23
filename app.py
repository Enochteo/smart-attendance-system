from flask import Flask, render_template, Response, send_file
import os
import cv2
import csv
from datetime import datetime
from face_recog_utils import detect_and_log_face

app = Flask(__name__)
camera = cv2.VideoCapture(0)  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"attendance_{date_str}.csv"
    data = []
    if os.path.exists(filename):
        with open(filename, "r") as file:
            reader = csv.reader(file)
            next(reader)
            data = list(reader)
    return render_template("admin.html", data=data)

@app.route("/download")
def download_csv():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"attendance_{date_str}.csv"
    return send_file(filename, as_attachment=True)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Apply detection here
            frame = detect_and_log_face(frame)

            # Encode and yield frame to browser
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/preview_feed')
def preview_feed():
    def gen_preview():
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if not success:
                break
            ret, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(gen_preview(), mimetype="multipart/x-mixed-replace; boundary=frame")
if __name__ == "__main__":
    app.run(debug=True)
