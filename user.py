from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import redirect, url_for
from decorators import user_required

user = Blueprint('user', __name__)

@user.route('/user/dashboard')
@login_required
@user_required
def dashboard():
    if current_user.role != 'user':
        return redirect(url_for('auth.dashboard_redirect'))
    return render_template('user/dashboard.html')