from app import db
from datetime import datetime

# --- Users Table ---
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id'), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# --- Doctors Table ---
class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id'), nullable=False)

# --- Local Admins Table ---
class LocalAdmin(db.Model):
    __tablename__ = 'local_admins'
    local_admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id'), nullable=False)

# --- Global Admins Table ---
class GlobalAdmin(db.Model):
    __tablename__ = 'global_admins'
    global_admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

# --- Clinics Table ---
class Clinic(db.Model):
    __tablename__ = 'clinics'
    clinic_id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(150), nullable=False)
    clinic_address = db.Column(db.String(250), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)

    users = db.relationship('User', backref='clinic', lazy=True)

# --- Global Admin Access Table ---
class GlobalAdminAccess(db.Model):
    __tablename__ = 'global_admin_access'
    global_admin_id = db.Column(db.Integer, db.ForeignKey('global_admins.global_admin_id'), primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id'), primary_key=True)

# --- Patients Table ---
class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(150), nullable=False)
    patient_contact = db.Column(db.String(20), nullable=False)
    data_of_birth = db.Column(db.Date, nullable=False)

# --- Patient Access Control Table ---
class PatientAccessControl(db.Model):
    __tablename__ = 'patient_access_control'
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id'), primary_key=True)

# --- Images Table (For Storing Image Metadata) ---
class Image(db.Model):
    __tablename__ = 'images'
    image_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Local file storage
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

# --- Reports Table ---
class Report(db.Model):
    __tablename__ = 'reports'
    report_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.image_id'), nullable=False)
    prediction_result = db.Column(db.String(50), nullable=False)
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)
