from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):  
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'global_admin', 'local_admin', 'doctor'

    clinic_relationships = db.relationship('UserClinicMap', backref='user')
    processed_applications = db.relationship('ClinicRegistration', backref='processed_by_user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Clinic(db.Model):
    __tablename__ = 'clinics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    license_number = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    
    user_relationships = db.relationship('UserClinicMap', backref='clinic')
    patient_relationships = db.relationship('PatientClinicMap', backref='clinic')

class UserClinicMap(db.Model):
    __tablename__ = 'user_clinic_map'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    role_at_clinic = db.Column(db.String(20))  # 'local_admin', 'doctor'

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    
    clinic_relationships = db.relationship('PatientClinicMap', backref='patient')
    images = db.relationship('Image', backref='patient')

class PatientClinicMap(db.Model):
    __tablename__ = 'patient_clinic_map'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    prediction_result = db.Column(db.String(50), nullable=False)
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)

class ClinicRegistration(db.Model):
    __tablename__ = 'clinic_registrations'
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(150), nullable=False)
    clinic_address = db.Column(db.String(250), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    admin_name = db.Column(db.String(100), nullable=False)
    admin_email = db.Column(db.String(120), nullable=False, unique=True)
    admin_phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50), nullable=False)
    license_document = db.Column(db.String(255), nullable=False)
    doctor_count = db.Column(db.Integer, default=1)
    doctor_names = db.Column(db.Text)  # JSON string
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejection_reason = db.Column(db.Text)
    
    def get_doctor_list(self):
        try:
            return json.loads(self.doctor_names) if self.doctor_names else {}
        except json.JSONDecodeError:
            return {}