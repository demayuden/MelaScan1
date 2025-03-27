from flask import Flask
import os
from app.extensions import db, migrate, bcrypt
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf  

# Import blueprints
from app.routes.home import home_bp
from app.routes.auth import registration_bp
from app.routes.auth import auth_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///D:\MelaScan1\instance\mela_scan.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload folders
    app.config['UPLOAD_FOLDERS'] = {
        'registration': os.getenv('UPLOAD_FOLDER_REGISTRATION'),
        'reports': os.getenv('UPLOAD_FOLDER_REPORTS')
    }
    
    # Create upload directories
    for folder in app.config['UPLOAD_FOLDERS'].values():
        os.makedirs(folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Inject CSRF token into all templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)  # Now properly imported
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(registration_bp, url_prefix='/registration')
    app.register_blueprint(auth_bp, url_prefix='/auth')


    return app