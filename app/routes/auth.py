"""
Authentication routes - login, logout, 2FA, password reset
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with various challenges"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # For AJAX validation
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        captcha_answer = request.form.get('captcha_answer', '')
        
        # Validate captcha
        expected_captcha = session.get('captcha_answer')
        if expected_captcha and str(captcha_answer) != str(expected_captcha):
            return {'success': False, 'error': 'Nieprawidłowa odpowiedź captcha'}, 400
        
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            return {'success': False, 'error': 'Nieprawidłowy login lub hasło'}, 401
        
        if user.is_locked:
            return {'success': False, 'error': 'Konto jest zablokowane', 'locked': True}, 403
        
        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 3:
                user.is_locked = True
            db.session.commit()
            
            remaining = 3 - user.failed_login_attempts
            if remaining > 0:
                return {'success': False, 'error': f'Nieprawidłowy login lub hasło. Pozostało prób: {remaining}'}, 401
            else:
                return {'success': False, 'error': 'Konto zostało zablokowane', 'locked': True}, 403
        
        # Successful password check - reset failed attempts
        user.failed_login_attempts = 0
        db.session.commit()
        
        # Check if 2FA required
        if user.require_2fa:
            session['pending_user_id'] = user.id
            return {'success': True, 'redirect': url_for('auth.two_factor')}, 200
        
        # Check if password expired
        if user.password_expired:
            session['pending_user_id'] = user.id
            return {'success': True, 'redirect': url_for('auth.change_password')}, 200
        
        # Login successful
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        return {'success': True, 'redirect': next_page or url_for('dashboard.index')}, 200
    
    # Regular GET request
    import random
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_answer'] = num1 + num2
    
    return render_template('auth/login.html', captcha_num1=num1, captcha_num2=num2)


@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """Two-factor authentication page"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        code = request.form.get('code', '')
        
        # Check 2FA code (in real app this would be TOTP)
        if code == '123456':
            user = User.query.get(session['pending_user_id'])
            if user:
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                session.pop('pending_user_id', None)
                flash('Zalogowano pomyślnie!', 'success')
                return redirect(url_for('dashboard.index'))
        
        flash('Nieprawidłowy kod weryfikacyjny', 'error')
    
    return render_template('auth/two_factor.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Force password change for expired passwords"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if len(new_password) < 8:
            flash('Hasło musi mieć co najmniej 8 znaków', 'error')
        elif new_password != confirm_password:
            flash('Hasła nie są identyczne', 'error')
        else:
            user = User.query.get(session['pending_user_id'])
            if user:
                user.set_password(new_password)
                user.password_expired = False
                db.session.commit()
                
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                session.pop('pending_user_id', None)
                
                flash('Hasło zostało zmienione. Zalogowano pomyślnie!', 'success')
                return redirect(url_for('dashboard.index'))
    
    return render_template('auth/change_password.html')


@auth_bp.route('/locked')
def locked_account():
    """Locked account information page"""
    return render_template('auth/locked_account.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('Wylogowano pomyślnie', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/check-session')
def check_session():
    """AJAX endpoint to check session validity (for timeout testing)"""
    if current_user.is_authenticated:
        return {'valid': True}, 200
    return {'valid': False}, 401
