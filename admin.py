from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import redirect, url_for
from decorators import admin_required

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('auth.dashboard_redirect'))
    return render_template('admin/dashboard.html')