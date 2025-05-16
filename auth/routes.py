import logging
import uuid
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from config import Config

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def generate_api_key():
    """Generate a unique API key"""
    return str(uuid.uuid4())

def validate_api_key(f):
    """Decorator to validate API key for API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers or query parameters
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({"error": "API key is required"}), 401
        
        # Find user with this API key
        user = User.query.filter_by(api_key=api_key).first()
        
        if not user:
            return jsonify({"error": "Invalid API key"}), 401
        
        # Set current user for the request
        login_user(user)
        
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                api_key=generate_api_key()
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            flash('An error occurred during registration', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login a user"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.login'))
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log user in
        login_user(user, remember=remember)
        
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout a user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/api-key', methods=['GET'])
@login_required
def get_api_key():
    """Get the user's API key"""
    return jsonify({
        "api_key": current_user.api_key
    }), 200

@auth_bp.route('/api-key/regenerate', methods=['POST'])
@login_required
def regenerate_api_key():
    """Regenerate the user's API key"""
    try:
        current_user.api_key = generate_api_key()
        db.session.commit()
        
        return jsonify({
            "message": "API key regenerated successfully",
            "api_key": current_user.api_key
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error regenerating API key: {str(e)}")
        return jsonify({"error": f"Failed to regenerate API key: {str(e)}"}), 500
