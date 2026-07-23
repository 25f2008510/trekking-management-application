from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, StaffProfile

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Contact admin.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user.role == 'staff':
            staff_profile = StaffProfile.query.filter_by(user_id=user.id).first()
            if not staff_profile or not staff_profile.is_approved:
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))
            if staff_profile.is_blacklisted:
                flash('Your account has been blacklisted. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('auth.dashboard_redirect'))
    
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        if role not in ['staff', 'user']:
            flash('Invalid role selected', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        
        if role == 'staff':
            staff_profile = StaffProfile(user_id=new_user.id)
            db.session.add(staff_profile)
            db.session.commit()
            flash('Registration successful. Wait for admin approval.', 'warning')
        else:
            flash('Registration successful. Please login.', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/dashboard')
@login_required
def dashboard_redirect():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'staff':
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('user.dashboard'))