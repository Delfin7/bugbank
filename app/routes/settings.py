"""
Settings routes - user profile and preferences
"""

import os
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User
import time
import random

settings_bp = Blueprint('settings', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@settings_bp.route('/settings')
@login_required
def profile():
    """Settings/Profile page"""
    return render_template('settings/profile.html', user=current_user)


@settings_bp.route('/api/settings/profile', methods=['GET'])
@login_required
def get_profile():
    """API: Get profile data"""
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'phone': current_user.phone,
        'language': current_user.language,
        'notifications_enabled': current_user.notifications_enabled,
        'avatar': current_user.avatar
    })


@settings_bp.route('/api/settings/profile', methods=['POST'])
@login_required
def update_profile():
    """API: Update profile data"""
    data = request.json
    
    errors = []
    
    # Validate email
    new_email = data.get('email', '').strip()
    if new_email and new_email != current_user.email:
        if '@' not in new_email:
            errors.append('Nieprawidłowy adres email')
        elif User.query.filter_by(email=new_email).first():
            errors.append('Ten adres email jest już zajęty')
        else:
            current_user.email = new_email
    
    # Update other fields
    if 'first_name' in data:
        current_user.first_name = data['first_name'].strip()
    
    if 'last_name' in data:
        current_user.last_name = data['last_name'].strip()
    
    if 'phone' in data:
        current_user.phone = data['phone'].strip()
    
    if 'language' in data:
        current_user.language = data['language']
    
    if 'notifications_enabled' in data:
        current_user.notifications_enabled = data['notifications_enabled']
    
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Profil zaktualizowany'})


@settings_bp.route('/api/settings/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """API: Upload avatar image"""
    if 'avatar' not in request.files:
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Niedozwolony format pliku. Użyj: PNG, JPG, GIF'}), 400
    
    # Simulate upload delay
    time.sleep(random.uniform(0.5, 1.5))
    
    filename = secure_filename(f"avatar_{current_user.id}_{file.filename}")
    
    # In real app, save to disk or cloud storage
    # For training purposes, just update the filename in DB
    current_user.avatar = filename
    db.session.commit()
    
    return jsonify({
        'success': True,
        'avatar': filename,
        'message': 'Avatar zaktualizowany'
    })


@settings_bp.route('/api/settings/password', methods=['POST'])
@login_required
def change_password():
    """API: Change password"""
    data = request.json
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    errors = []
    
    if not current_user.check_password(current_password):
        errors.append('Nieprawidłowe obecne hasło')
    
    if len(new_password) < 8:
        errors.append('Nowe hasło musi mieć co najmniej 8 znaków')
    
    if new_password != confirm_password:
        errors.append('Hasła nie są identyczne')
    
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Hasło zmienione'})


@settings_bp.route('/api/settings/notifications-order', methods=['POST'])
@login_required
def update_notifications_order():
    """API: Update notification preferences order (for drag&drop testing)"""
    order = request.json.get('order', [])
    
    # In real app, this would save the order to user preferences
    # For training purposes, just acknowledge
    time.sleep(random.uniform(0.3, 0.8))
    
    return jsonify({
        'success': True,
        'order': order,
        'message': 'Kolejność powiadomień zaktualizowana'
    })


@settings_bp.route('/api/settings/delete-account', methods=['POST'])
@login_required
def delete_account():
    """API: Delete user account (requires confirmation)"""
    confirmation = request.json.get('confirmation', '')
    
    if confirmation != 'USUŃ KONTO':
        return jsonify({
            'success': False,
            'error': 'Wpisz "USUŃ KONTO" aby potwierdzić'
        }), 400
    
    # In real app, this would actually delete the account
    # For training purposes, just simulate
    time.sleep(1)
    
    return jsonify({
        'success': True,
        'message': 'Konto zostało usunięte',
        'redirect': '/logout'
    })
