from flask import Flask, render_template, Response, send_file, url_for, flash, redirect, request
import os
import cv2
import csv
import time
import numpy as np
from werkzeug.utils import secure_filename
from datetime import datetime
from face_recog_utils import detect_and_log_face, load_known_faces
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from models import db, Student, AttendanceLog
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
migrate = Migrate(app, db)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.secret_key = os.getenv("DATABASE_URL")

with app.app_context():
    db.create_all()

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
    total = len(data)
    logs = AttendanceLog.query.order_by(AttendanceLog.timestamp.desc()).all()
    return render_template("admin.html", data=data, logs=logs, total=total)

@app.route("/download")
def download_csv():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"attendance_{date_str}.csv"
    return send_file(filename, as_attachment=True)

@app.route('/mark')
def mark_attendance_route():
    return render_template("mark.html")

@app.route('/success')
def success():
    return render_template("success.html")

def gen_frames():
    camera = cv2.VideoCapture(0)  
    try:   
        attendance_done = False

        while True:
            success, frame = camera.read()
            if not success:
                break
            with app.app_context():
                frame, attendance_done = detect_and_log_face(frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            if attendance_done:
                frame = np.zeros((300, 600, 3), dtype=np.uint8)
                cv2.putText(frame, "Attendance Marked!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                time.sleep(2)
                break
    except Exception as e:
        print("[ERROR] Stream crashed:", str(e))
    finally:    
        camera.release()
        cv2.destroyAllWindows()


    camera.release()
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/preview_feed')
def preview_feed():
    def gen_preview():
        cap = cv2.VideoCapture(0)
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break
                ret, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            cap.release()
            cv2.destroyAllWindows()
    return Response(gen_preview(), mimetype="multipart/x-mixed-replace; boundary=frame")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        name = request.form.get("name", "").strip()
        gnumber = request.form.get("gnumber", "").strip()

        if not name or not name.isalpha():
            flash("Invalid name. Please add no space")
            return redirect(request.url)
        if not gnumber or not gnumber.startswith("G"):
            flash("Invalid GNumber. Must start with a 'G' .")
            return redirect(request.url)

        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            existing_student = Student.query.filter_by(gnumber=gnumber).first()
            if existing_student:
                flash(f"A student with GNumber {gnumber} already exists.")
                return redirect(request.url)
            # Save file using format: G12345678-Name.jpg
            filename = secure_filename(f"{gnumber}-{name}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # DB insert
            student = Student(name=name, image_filename=filename, gnumber=gnumber)
            db.session.add(student)
            db.session.commit()

            # Reload known faces
            global known_encodings, names, gnumbers
            known_encodings, names, gnumbers = load_known_faces()

            flash('Upload successful!')
            return redirect(url_for('upload_image'))

    return render_template('upload.html')

if __name__ == "__main__":
    app.run(debug=True)
