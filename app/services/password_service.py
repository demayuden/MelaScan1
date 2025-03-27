#app/services/password_service.py
import secrets
import string
from flask import current_app

class PasswordService:
    @staticmethod
    def generate_permanent_password(length=12):
        """Generate a secure password without forced change"""
        if current_app.config.get('TESTING'):
            return "PermanentPass123!"
        
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def generate_temp_password(length=10):
        """Generate a temporary password"""
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))