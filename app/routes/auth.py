from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os
import json
from datetime import datetime
from app.forms import ClinicRegistrationForm, LoginForm
from app.models import ClinicRegistration, User, Clinic, UserClinicMap
from app.extensions import db
from app.services.email_service import send_credentials_email
from app.services.password_service import PasswordService

registration_bp = Blueprint('registration', __name__)
auth_bp = Blueprint('auth', __name__)

# Simple admin check (replace with your preferred method)
def is_admin():
    return session.get('is_admin', False)

@registration_bp.route('/register/clinic', methods=['GET', 'POST'])
def clinic_registration():
    form = ClinicRegistrationForm()
    
    if request.method == 'POST':
        try:
            doctor_count = int(request.form.get('doctor_count', 1))
            form.doctors.entries = doctor_count
        except (ValueError, KeyError):
            form.doctors.entries = 1
    
    if form.validate_on_submit():
        try:
            license_file = form.license_document.data
            filename = secure_filename(license_file.filename)
            upload_folder = 'uploads'  # Simplified static folder
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            license_file.save(file_path)
            
            doctors_data = {}
            for doctor in form.doctors:
                if doctor.name.data and doctor.email.data:
                    doctors_data[doctor.name.data] = doctor.email.data
            
            registration = ClinicRegistration(
                clinic_name=form.clinic_name.data,
                clinic_address=form.clinic_address.data,
                contact_number=form.contact_number.data,
                admin_name=form.admin_name.data,
                admin_email=form.admin_email.data,
                admin_phone=form.admin_phone.data,
                license_number=form.license_number.data,
                license_document=file_path,
                doctor_count=len(doctors_data),
                doctor_names=json.dumps(doctors_data),
                status='pending'
            )
            
            db.session.add(registration)
            db.session.commit()
            
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('registration.track_application', application_id=registration.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('registration/clinic_register.html', form=form)

@registration_bp.route('/admin/process_registration/<int:application_id>', methods=['POST'])
def process_registration(application_id):
    if not is_admin():
        return "Unauthorized", 403
    
    application = ClinicRegistration.query.get_or_404(application_id)
    
    if request.form.get('action') == 'approve':
        try:
            clinic = Clinic(
                name=application.clinic_name,
                address=application.clinic_address,
                contact_number=application.contact_number,
                license_number=application.license_number,
                status='active'
            )
            db.session.add(clinic)
            db.session.flush()
            
            admin_password = PasswordService.generate_permanent_password()
            admin = User(
                username=application.admin_email.split('@')[0],
                email=application.admin_email,
                role='local_admin'
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.flush()
            
            doctors = json.loads(application.doctor_names)
            for name, email in doctors.items():
                doctor_password = PasswordService.generate_permanent_password()
                doctor = User(
                    username=email.split('@')[0],
                    email=email,
                    role='doctor'
                )
                doctor.set_password(doctor_password)
                db.session.add(doctor)
                db.session.flush()
                
                db.session.add(UserClinicMap(
                    user_id=doctor.id,
                    clinic_id=clinic.id,
                    role_at_clinic='doctor'
                ))
                
                send_credentials_email(email, clinic.name, doctor_password)
            
            db.session.add(UserClinicMap(
                user_id=admin.id,
                clinic_id=clinic.id,
                role_at_clinic='admin'
            ))
            
            application.status = 'approved'
            application.processed_at = datetime.utcnow()
            application.processed_by = session.get('user_id')  # Simple session ID
            
            db.session.commit()
            
            send_credentials_email(application.admin_email, clinic.name, admin_password)
            flash('Clinic approved successfully', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Approval failed: {str(e)}', 'danger')
    
    elif request.form.get('action') == 'reject':
        rejection_reason = request.form.get('rejection_reason')
        if not rejection_reason:
            flash('Please provide a rejection reason', 'danger')
            return redirect(url_for('registration.process_registration', application_id=application_id))
        
        application.status = 'rejected'
        application.rejection_reason = rejection_reason
        application.processed_at = datetime.utcnow()
        application.processed_by = session.get('user_id')
        db.session.commit()
        
        flash('Application rejected', 'success')
    
    return redirect(url_for('registration.admin_view_registrations'))

@registration_bp.route('/admin/registrations')
def admin_view_registrations():
    if not is_admin():
        return "Unauthorized", 403
    
    applications = ClinicRegistration.query.filter_by(status='pending').all()
    return render_template('registration/registrations.html', applications=applications)

@registration_bp.route('/track/<int:application_id>')
def track_application(application_id):
    application = ClinicRegistration.query.get_or_404(application_id)
    return render_template('registration/track_application.html', application=application)



## LOG IN ##
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['username'] = user.username
            
            flash('Login successful!', 'success')
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'local_admin':
                return redirect(url_for('clinic.dashboard'))
            else:
                return redirect(url_for('doctor.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home.home'))