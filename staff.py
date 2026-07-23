from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import redirect, url_for
from decorators import staff_required

staff = Blueprint('staff', __name__)

@staff.route('/staff/dashboard')
@login_required
@staff_required
def dashboard():
    if current_user.role != 'staff':
        return redirect(url_for('auth.dashboard_redirect'))
    return render_template('staff/dashboard.html')