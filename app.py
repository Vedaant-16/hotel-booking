from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, date, timedelta
import sqlite3
import database as db

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

@app.route('/')
def index():
    """Home page - show available rooms"""
    conn = db.get_db()
    rooms = conn.execute('''
        SELECT * FROM rooms 
        WHERE status = 'available'
        ORDER BY room_number
    ''').fetchall()
    conn.close()
    return render_template('index.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Staff login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = db.get_db()
        staff = conn.execute('''
            SELECT * FROM staff WHERE username = ?
        ''', (username,)).fetchone()
        conn.close()
        
        if staff and db.verify_password(password, staff['password_hash']):
            session['user_id'] = staff['staff_id']
            session['username'] = staff['username']
            session['role'] = staff['role']
            session['name'] = f"{staff['first_name']} {staff['last_name']}"
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Staff sign up page"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate required fields
        if not all([first_name, last_name, email, phone, role, username, password]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('login'))
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('login'))
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('login'))
        
        password_hash = db.hash_password(password)
        
        conn = db.get_db()
        try:
            conn.execute('''
                INSERT INTO staff (first_name, last_name, email, phone, role, username, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, phone, role, username, password_hash))
            conn.commit()
            conn.close()
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Username or email already exists', 'error')
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/check_availability', methods=['POST'])
def check_availability():
    """Check room availability for given dates"""
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    
    if not check_in or not check_out:
        return jsonify({'error': 'Please provide check-in and check-out dates'}), 400
    
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        if check_out_date <= check_in_date:
            return jsonify({'error': 'Check-out date must be after check-in date'}), 400
        
        if check_in_date < date.today():
            return jsonify({'error': 'Check-in date cannot be in the past'}), 400
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    conn = db.get_db()
    available_rooms = []
    
    all_rooms = conn.execute('SELECT * FROM rooms WHERE status != "maintenance"').fetchall()
    
    for room in all_rooms:
        if db.check_room_availability(room['room_id'], check_in, check_out):
            total_amount = db.calculate_total_amount(room['room_id'], check_in, check_out)
            room_dict = dict(room)
            room_dict['total_amount'] = total_amount
            available_rooms.append(room_dict)
    
    conn.close()
    return jsonify({'rooms': available_rooms})

@app.route('/book', methods=['GET', 'POST'])
def book():
    """Book a room"""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        room_id = request.form.get('room_id')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        number_of_guests = request.form.get('number_of_guests')
        special_requests = request.form.get('special_requests', '')
        
        # Validate
        if not all([first_name, last_name, email, phone, room_id, check_in, check_out, number_of_guests]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('book'))
        
        # Check availability
        if not db.check_room_availability(room_id, check_in, check_out):
            flash('Room is not available for the selected dates', 'error')
            return redirect(url_for('book'))
        
        conn = db.get_db()
        
        # Get or create customer
        customer = conn.execute('SELECT customer_id FROM customers WHERE email = ?', (email,)).fetchone()
        if customer:
            customer_id = customer['customer_id']
            # Update customer info
            conn.execute('''
                UPDATE customers SET first_name = ?, last_name = ?, phone = ?
                WHERE customer_id = ?
            ''', (first_name, last_name, phone, customer_id))
        else:
            cursor = conn.execute('''
                INSERT INTO customers (first_name, last_name, email, phone)
                VALUES (?, ?, ?, ?)
            ''', (first_name, last_name, email, phone))
            customer_id = cursor.lastrowid
        
        # Calculate total amount
        total_amount = db.calculate_total_amount(room_id, check_in, check_out)
        
        # Create booking
        cursor = conn.execute('''
            INSERT INTO bookings (customer_id, room_id, check_in_date, check_out_date, 
                                number_of_guests, total_amount, special_requests, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (customer_id, room_id, check_in, check_out, number_of_guests, total_amount, special_requests))
        
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash(f'Booking created successfully! Booking ID: {booking_id}', 'success')
        return redirect(url_for('payment', booking_id=booking_id))
    
    # GET request - show booking form
    room_id = request.args.get('room_id')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    
    conn = db.get_db()
    room = None
    if room_id:
        room = conn.execute('SELECT * FROM rooms WHERE room_id = ?', (room_id,)).fetchone()
    conn.close()
    
    return render_template('book.html', room=room, check_in=check_in, check_out=check_out)

@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    """Payment page"""
    conn = db.get_db()
    booking = conn.execute('''
        SELECT b.*, r.room_number, r.room_type, c.first_name, c.last_name, c.email
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    conn.close()
    
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('Please select a payment method', 'error')
            return redirect(url_for('payment', booking_id=booking_id))
        
        conn = db.get_db()
        
        # Create payment record
        conn.execute('''
            INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_id)
            VALUES (?, ?, ?, 'completed', ?)
        ''', (booking_id, booking['total_amount'], payment_method, f'TXN{booking_id}{datetime.now().strftime("%Y%m%d%H%M%S")}'))
        
        # Update booking status
        conn.execute('''
            UPDATE bookings SET status = 'confirmed' WHERE booking_id = ?
        ''', (booking_id,))
        
        conn.commit()
        conn.close()
        
        flash('Payment successful! Your booking is confirmed.', 'success')
        return redirect(url_for('booking_confirmation', booking_id=booking_id))
    
    return render_template('payment.html', booking=booking)

@app.route('/booking_confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    """Booking confirmation page"""
    conn = db.get_db()
    booking = conn.execute('''
        SELECT b.*, r.room_number, r.room_type, c.*, p.payment_method, p.transaction_id
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        JOIN customers c ON b.customer_id = c.customer_id
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    conn.close()
    
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('confirmation.html', booking=booking)

@app.route('/admin')
@db.login_required
def admin_dashboard():
    """Admin dashboard"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    conn = db.get_db()
    
    # Statistics
    total_rooms = conn.execute('SELECT COUNT(*) as count FROM rooms').fetchone()['count']
    available_rooms = conn.execute("SELECT COUNT(*) as count FROM rooms WHERE status = 'available'").fetchone()['count']
    total_bookings = conn.execute('SELECT COUNT(*) as count FROM bookings').fetchone()['count']
    pending_bookings = conn.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'").fetchone()['count']
    total_revenue = conn.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_status = 'completed'").fetchone()['total']
    
    # Recent bookings
    recent_bookings = conn.execute('''
        SELECT b.*, r.room_number, r.room_type, c.first_name, c.last_name, c.email
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         total_rooms=total_rooms,
                         available_rooms=available_rooms,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings)

@app.route('/admin/rooms')
@db.admin_required
def admin_rooms():
    """Manage rooms"""
    conn = db.get_db()
    rooms = conn.execute('SELECT * FROM rooms ORDER BY room_number').fetchall()
    conn.close()
    return render_template('admin/rooms.html', rooms=rooms)

@app.route('/admin/rooms/add', methods=['GET', 'POST'])
@db.admin_required
def add_room():
    """Add new room"""
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        room_type = request.form.get('room_type')
        price_per_night = request.form.get('price_per_night')
        capacity = request.form.get('capacity')
        amenities = request.form.get('amenities', '')
        status = request.form.get('status', 'available')
        
        conn = db.get_db()
        try:
            conn.execute('''
                INSERT INTO rooms (room_number, room_type, price_per_night, capacity, amenities, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (room_number, room_type, price_per_night, capacity, amenities, status))
            conn.commit()
            flash('Room added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Room number already exists', 'error')
        conn.close()
        return redirect(url_for('admin_rooms'))
    
    return render_template('admin/add_room.html')

@app.route('/admin/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@db.admin_required
def edit_room(room_id):
    """Edit room"""
    conn = db.get_db()
    
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        room_type = request.form.get('room_type')
        price_per_night = request.form.get('price_per_night')
        capacity = request.form.get('capacity')
        amenities = request.form.get('amenities', '')
        status = request.form.get('status')
        
        conn.execute('''
            UPDATE rooms SET room_number = ?, room_type = ?, price_per_night = ?, 
                           capacity = ?, amenities = ?, status = ?
            WHERE room_id = ?
        ''', (room_number, room_type, price_per_night, capacity, amenities, status, room_id))
        conn.commit()
        conn.close()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('admin_rooms'))
    
    room = conn.execute('SELECT * FROM rooms WHERE room_id = ?', (room_id,)).fetchone()
    conn.close()
    
    if not room:
        flash('Room not found', 'error')
        return redirect(url_for('admin_rooms'))
    
    return render_template('admin/edit_room.html', room=room)

@app.route('/admin/rooms/delete/<int:room_id>')
@db.admin_required
def delete_room(room_id):
    """Delete room"""
    conn = db.get_db()
    conn.execute('DELETE FROM rooms WHERE room_id = ?', (room_id,))
    conn.commit()
    conn.close()
    flash('Room deleted successfully!', 'success')
    return redirect(url_for('admin_rooms'))

@app.route('/admin/bookings')
@db.admin_required
def admin_bookings():
    """Manage bookings"""
    conn = db.get_db()
    bookings = conn.execute('''
        SELECT b.*, r.room_number, r.room_type, c.first_name, c.last_name, c.email, c.phone
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/bookings/update_status/<int:booking_id>', methods=['POST'])
@db.admin_required
def update_booking_status(booking_id):
    """Update booking status"""
    new_status = request.form.get('status')
    
    conn = db.get_db()
    conn.execute('UPDATE bookings SET status = ? WHERE booking_id = ?', (new_status, booking_id))
    
    # If checking in, update room status
    if new_status == 'checked_in':
        booking = conn.execute('SELECT room_id FROM bookings WHERE booking_id = ?', (booking_id,)).fetchone()
        if booking:
            conn.execute('UPDATE rooms SET status = "occupied" WHERE room_id = ?', (booking['room_id'],))
    
    # If checking out, update room status and create payment if needed
    if new_status == 'checked_out':
        booking = conn.execute('SELECT room_id FROM bookings WHERE booking_id = ?', (booking_id,)).fetchone()
        if booking:
            conn.execute('UPDATE rooms SET status = "available" WHERE room_id = ?', (booking['room_id'],))
        
        # Check if payment exists
        payment = conn.execute('SELECT payment_id FROM payments WHERE booking_id = ?', (booking_id,)).fetchone()
        if not payment:
            booking_info = conn.execute('SELECT total_amount FROM bookings WHERE booking_id = ?', (booking_id,)).fetchone()
            conn.execute('''
                INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_id)
                VALUES (?, ?, 'cash', 'completed', ?)
            ''', (booking_id, booking_info['total_amount'], f'TXN{booking_id}{datetime.now().strftime("%Y%m%d%H%M%S")}'))
    
    conn.commit()
    conn.close()
    flash('Booking status updated successfully!', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/staff')
@db.admin_required
def admin_staff():
    """Manage staff"""
    conn = db.get_db()
    staff_members = conn.execute('SELECT * FROM staff ORDER BY role, last_name').fetchall()
    conn.close()
    return render_template('admin/staff.html', staff=staff_members)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@db.admin_required
def add_staff():
    """Add new staff member"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        
        password_hash = db.hash_password(password)
        
        conn = db.get_db()
        try:
            conn.execute('''
                INSERT INTO staff (first_name, last_name, email, phone, role, username, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, phone, role, username, password_hash))
            conn.commit()
            flash('Staff member added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'error')
        conn.close()
        return redirect(url_for('admin_staff'))
    
    return render_template('admin/add_staff.html')

@app.route('/admin/staff/delete/<int:staff_id>')
@db.admin_required
def delete_staff(staff_id):
    """Delete staff member"""
    if staff_id == session.get('user_id'):
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin_staff'))
    
    conn = db.get_db()
    conn.execute('DELETE FROM staff WHERE staff_id = ?', (staff_id,))
    conn.commit()
    conn.close()
    flash('Staff member deleted successfully!', 'success')
    return redirect(url_for('admin_staff'))

if __name__ == '__main__':
    # Initialize database on first run
    import os
    if not os.path.exists('hotel_booking.db'):
        db.init_db()
        print("Database initialized!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

