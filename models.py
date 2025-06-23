from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_filename = db.Column(db.String(100), nullable=False)
    gnumber = db.Column(db.String(20), unique=True, nullable=False)
    logs = db.relationship('AttendanceLog', backref='student', lazy=True)

class AttendanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(10), nullable=False)
