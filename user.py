from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from decorators import user_required
from models import db, Trek, Booking, User


user = Blueprint('user', __name__)

@user.route('/user/dashboard')
@login_required
@user_required       #dashboard route
def dashboard():
    if current_user.role != 'user':
        return redirect(url_for('auth.dashboard_redirect'))

    open_treks = Trek.query.filter_by(status='Open').order_by(Trek.start_date.asc()).all()
    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()

    return render_template('user/dashboard.html',
                            open_treks=open_treks,
                            my_bookings=my_bookings)

@user.route('/user/treks')
@login_required       #browse/search treks route
@user_required
def browse_treks():
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()

    query = Trek.query.filter_by(status='Open')

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    treks_list = query.order_by(Trek.start_date.asc()).all()

    return render_template('user/browse_treks.html',
                            treks=treks_list,
                            difficulty=difficulty,
                            location=location)

@user.route('/user/treks/book/<int:trek_id>', methods=['POST'])
@login_required       #book trek route
@user_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.status != 'Open':
        flash('This trek is not available for booking.', 'danger')
        return redirect(url_for('user.browse_treks'))

    if trek.available_slots <= 0:
        flash('No slots left in this trek.', 'danger')
        return redirect(url_for('user.browse_treks'))

    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
    ).first()
    if existing:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('user.browse_treks'))

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
    )
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()

    flash('Trek booked successfully!!!!!!', 'success')
    return redirect(url_for('user.dashboard'))

@user.route('/user/bookings/cancel/<int:booking_id>', methods=['POST'])
@login_required      #cancel booking route
@user_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('You do not have permission to cancel this booking.', 'danger')
        return redirect(url_for('user.dashboard'))

    if booking.status != 'Booked':
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('user.dashboard'))

    booking.status = 'Cancelled'
    booking.trek.available_slots += 1
    db.session.commit()

    flash('Booking cancelled.', 'success')
    return redirect(url_for('user.dashboard'))

@user.route('/user/history')
@login_required      #history route
@user_required
def history():
    all_bookings = Booking.query.filter_by(user_id=current_user.id) \
                                 .order_by(Booking.booking_date.desc()).all()

    return render_template('user/history.html', bookings=all_bookings)

@user.route('/user/profile', methods=['GET', 'POST'])
@login_required   #user profile route
@user_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        if email != current_user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('That email is already in use.', 'danger')
                return redirect(url_for('user.profile'))

        current_user.name = name
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully!!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html')

@user.route('/user/treks/<int:trek_id>')
@login_required      #trek detail route
@user_required
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    already_booked = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
    ).first() is not None

    staff_member = User.query.get(trek.staff_id) if trek.staff_id else None

    return render_template('user/trek_detail.html',
                            trek=trek,
                            already_booked=already_booked,
                            staff_member=staff_member)