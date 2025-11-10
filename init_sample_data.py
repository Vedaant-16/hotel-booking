"""
Script to initialize the database with sample data
Run this after the database is created to populate it with sample rooms
"""

import sqlite3
import hashlib
from datetime import date, timedelta

DATABASE = 'hotel_booking.db'

def init_sample_data():
    """Initialize database with sample data"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Sample rooms
    sample_rooms = [
        ('101', 'Single', 50.00, 1, 'WiFi, TV, AC', 'available'),
        ('102', 'Single', 50.00, 1, 'WiFi, TV, AC', 'available'),
        ('201', 'Double', 80.00, 2, 'WiFi, TV, AC, Mini Bar', 'available'),
        ('202', 'Double', 80.00, 2, 'WiFi, TV, AC, Mini Bar', 'available'),
        ('301', 'Suite', 150.00, 4, 'WiFi, TV, AC, Mini Bar, Jacuzzi', 'available'),
        ('302', 'Suite', 150.00, 4, 'WiFi, TV, AC, Mini Bar, Jacuzzi', 'available'),
        ('401', 'Deluxe', 200.00, 2, 'WiFi, TV, AC, Mini Bar, Balcony, Ocean View', 'available'),
        ('402', 'Deluxe', 200.00, 2, 'WiFi, TV, AC, Mini Bar, Balcony, Ocean View', 'available'),
        ('501', 'Presidential', 500.00, 6, 'WiFi, TV, AC, Mini Bar, Jacuzzi, Balcony, Ocean View, Butler Service', 'available'),
    ]
    
    print("Adding sample rooms...")
    for room in sample_rooms:
        try:
            conn.execute('''
                INSERT INTO rooms (room_number, room_type, price_per_night, capacity, amenities, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', room)
            print(f"  Added room {room[0]}")
        except sqlite3.IntegrityError:
            print(f"  Room {room[0]} already exists, skipping...")
    
    conn.commit()
    conn.close()
    print("\nSample data initialization complete!")
    print("\nYou can now run the application with: python app.py")

if __name__ == '__main__':
    try:
        init_sample_data()
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("Make sure the database is initialized first by running app.py once.")

