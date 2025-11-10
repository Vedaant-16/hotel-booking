import sqlite3
import hashlib
from datetime import datetime, date
from functools import wraps
from flask import session, redirect, url_for

DATABASE = 'hotel_booking.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    
    # Create default admin user
    create_default_admin()

def create_default_admin():
    """Create default admin user"""
    conn = get_db()
    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    try:
        conn.execute('''
            INSERT INTO staff (first_name, last_name, email, phone, role, username, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Admin', 'User', 'admin@hotel.com', '1234567890', 'admin', 'admin', password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Admin already exists
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def check_room_availability(room_id, check_in, check_out):
    """Check if room is available for given dates"""
    conn = get_db()
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    
    # Check if room exists and is not in maintenance
    room = conn.execute('SELECT status FROM rooms WHERE room_id = ?', (room_id,)).fetchone()
    if not room or room['status'] == 'maintenance':
        conn.close()
        return False
    
    # Check for overlapping bookings
    overlapping = conn.execute('''
        SELECT COUNT(*) as count FROM bookings
        WHERE room_id = ? 
        AND status NOT IN ('cancelled', 'checked_out')
        AND (
            (check_in_date <= ? AND check_out_date > ?) OR
            (check_in_date < ? AND check_out_date >= ?) OR
            (check_in_date >= ? AND check_out_date <= ?)
        )
    ''', (room_id, check_in_date, check_in_date, check_out_date, check_out_date, check_in_date, check_out_date)).fetchone()
    
    conn.close()
    return overlapping['count'] == 0

def calculate_total_amount(room_id, check_in, check_out):
    """Calculate total amount for booking"""
    conn = get_db()
    room = conn.execute('SELECT price_per_night FROM rooms WHERE room_id = ?', (room_id,)).fetchone()
    conn.close()
    
    if not room:
        return 0
    
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    nights = (check_out_date - check_in_date).days
    
    return float(room['price_per_night']) * nights

