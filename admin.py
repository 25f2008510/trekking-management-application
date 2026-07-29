from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decorators import admin_required
from models import db, User, Trek, Booking, StaffProfile
from datetime import datetime

admin = Blueprint('admin', __name__)


@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    pending_staff = StaffProfile.query.filter_by(is_approved=False, is_blacklisted=False).count()

    return render_template('admin/dashboard.html',
                            total_treks=total_treks,
                            total_users=total_users,
                            total_staff=total_staff,
                            total_bookings=total_bookings,
                            pending_staff=pending_staff)


@admin.route('/admin/treks')
@login_required
@admin_required
def treks():
    query = request.args.get('q', '').strip()
    if query:
        treks_list = Trek.query.filter(Trek.name.ilike(f'%{query}%')).all()
    else:
        treks_list = Trek.query.order_by(Trek.created_at.desc()).all()
    return render_template('admin/treks.html', treks=treks_list, query=query)


@admin.route('/admin/treks/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_trek():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        total_slots = request.form.get('total_slots')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=int(duration),
            total_slots=int(total_slots),
            available_slots=int(total_slots),
            status='Pending',
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            description=description,
            created_by=current_user.id
        )
        db.session.add(trek)
        db.session.commit()
        flash('Trek created successfully.', 'success')
        return redirect(url_for('admin.treks'))

    return render_template('admin/trek_form.html', trek=None)


@admin.route('/admin/treks/edit/<int:trek_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        trek.total_slots = int(request.form.get('total_slots'))
        trek.status = request.form.get('status')
        trek.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        trek.description = request.form.get('description')

        db.session.commit()
        flash('Trek updated successfully.', 'success')
        return redirect(url_for('admin.treks'))

    return render_template('admin/trek_form.html', trek=trek)


@admin.route('/admin/treks/delete/<int:trek_id>', methods=['POST'])
@login_required
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.bookings:
        flash('Cannot delete this trek has existing bookings.', 'danger')
        return redirect(url_for('admin.treks'))

    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted.', 'success')
    return redirect(url_for('admin.treks'))


@admin.route('/admin/treks/assign/<int:trek_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    approved_staff = User.query.join(StaffProfile).filter(
        User.role == 'staff',
        StaffProfile.is_approved == True,
        StaffProfile.is_blacklisted == False
    ).all()

    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        trek.staff_id = int(staff_id) if staff_id else None
        db.session.commit()
        flash('Staff assigned successfully.', 'success')
        return redirect(url_for('admin.treks'))

    return render_template('admin/assign_staff.html', trek=trek, staff_list=approved_staff)


@admin.route('/admin/staff')
@login_required
@admin_required
def staff_list():
    query = request.args.get('q', '').strip()
    staff_q = User.query.filter_by(role='staff')
    if query:
        staff_q = staff_q.filter(User.name.ilike(f'%{query}%'))
    staff_members = staff_q.all()
    return render_template('admin/staff.html', staff_members=staff_members, query=query)


@admin.route('/admin/staff/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_staff(user_id):
    profile = StaffProfile.query.filter_by(user_id=user_id).first_or_404()
    profile.is_approved = True
    profile.is_blacklisted = False
    db.session.commit()
    flash('Staff approved.', 'success')
    return redirect(url_for('admin.staff_list'))


@admin.route('/admin/staff/blacklist/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def blacklist_staff(user_id):
    profile = StaffProfile.query.filter_by(user_id=user_id).first_or_404()
    profile.is_blacklisted = True
    profile.is_approved = False
    db.session.commit()
    flash('Staff blacklisted.', 'warning')
    return redirect(url_for('admin.staff_list'))


@admin.route('/admin/users')
@login_required
@admin_required
def users_list():
    query = request.args.get('q', '').strip()
    users_q = User.query.filter_by(role='user')
    if query:
        users_q = users_q.filter(User.name.ilike(f'%{query}%'))
    users = users_q.all()
    return render_template('admin/users.html', users=users, query=query)


@admin.route('/admin/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User {'activated' if user.is_active else 'blacklisted'}.", 'success')
    return redirect(url_for('admin.users_list'))


@admin.route('/admin/bookings')
@login_required
@admin_required
def bookings_list():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)