from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


# Import blueprints from other files
from app.routes.home import home_bp  # Import home blueprint

# Optionally, import other blueprints if required:
# from app.routes.auth import auth_bp
# from app.routes.clinic import clinic_bp
# from app.routes.patient import patient_bp
# from app.routes.image import image_bp
# from app.routes.report import report_bp


# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    print(f"Template Folder: {app.template_folder}")



    # Load configuration from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/MelaScan1/instance/mela_scan.db'


    # Register blueprints with the app
    app.register_blueprint(home_bp)  # Home page route without a url_prefix
    
    # Register other blueprints with url_prefixes as needed
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(clinic_bp, url_prefix='/clinic')
    # app.register_blueprint(patient_bp, url_prefix='/patient')
    # app.register_blueprint(image_bp, url_prefix='/image')
    # app.register_blueprint(report_bp, url_prefix='/report')

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    return app
