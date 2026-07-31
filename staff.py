from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decorators import staff_required
from models import db, Trek, Booking, StaffProfile
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

staff = Blueprint('staff', __name__)


@staff.route('/staff/dashboard')
@login_required
@staff_required
def dashboard():
    assigned_treks = Trek.query.filter_by(staff_id=current_user.id).order_by(Trek.start_date).all()

    trek_data = []
    for trek in assigned_treks:
        registered_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_data.append({'trek': trek, 'registered_count': registered_count})

    return render_template('staff/dashboard.html', trek_data=trek_data)


@staff.route('/staff/trek/<int:trek_id>')
@login_required
@staff_required
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/trek_detail.html', trek=trek, bookings=bookings)


@staff.route('/staff/trek/<int:trek_id>/update', methods=['POST'])
@login_required
@staff_required
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    available_slots = request.form.get('available_slots')
    status = request.form.get('status')

    if available_slots is not None:
        available_slots = int(available_slots)
        if available_slots > trek.total_slots:
            flash('Available slots cannot exceed total slots.', 'danger')
            return redirect(url_for('staff.trek_detail', trek_id=trek.id))
        trek.available_slots = available_slots

    if status in ['Open', 'Closed', 'Ongoing']:
        trek.status = status

    db.session.commit()
    flash('Trek updated successfully.', 'success')
    return redirect(url_for('staff.trek_detail', trek_id=trek.id))


@staff.route('/staff/profile', methods=['GET', 'POST'])
@login_required
@staff_required
def profile():
    staff_profile = StaffProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        current_user.name = request.form.get('name')
        staff_profile.phone = request.form.get('phone')
        staff_profile.experience = request.form.get('experience')

        new_password = request.form.get('new_password')
        if new_password:
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('staff.profile'))

    return render_template('staff/profile.html', staff_profile=staff_profile)


@staff.route('/staff/treks/complete/<int:trek_id>', methods=['POST'])
@login_required
@staff_required
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    if trek.status != 'Open':
        flash('Only an Open trek can be marked as Completed.', 'warning')
        return redirect(url_for('staff.trek_detail', trek_id=trek.id))

    trek.status = 'Completed'

    for booking in trek.bookings:
        if booking.status == 'Booked':
            booking.status = 'Completed'
            booking.completed_on = datetime.utcnow()

    db.session.commit()
    flash('Trek marked as completed.', 'success')
    return redirect(url_for('staff.trek_detail', trek_id=trek.id))