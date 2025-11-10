# Quick Start Guide

## Installation Steps

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application** (database will be created automatically):
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Optional: Add Sample Data

To populate the database with sample rooms, run:
```bash
python init_sample_data.py
```

This will add 9 sample rooms of different types (Single, Double, Suite, Deluxe, Presidential).

## Default Admin Login

- **URL**: http://localhost:5000/login
- **Username**: `admin`
- **Password**: `admin123`

## Testing the System

### As a User:
1. Visit the home page to see all available rooms
2. Use the "Check Availability" form to search for rooms by date
3. Click "Book Now" on any room
4. Fill in customer information and booking details
5. Complete the payment process
6. View your booking confirmation

### As an Admin:
1. Login with admin credentials
2. View the dashboard with statistics
3. Go to "Manage Rooms" to add/edit/delete rooms
4. Go to "Manage Bookings" to view and update booking statuses
5. Go to "Manage Staff" to add staff members

## Features to Test

- ✅ Browse all available rooms
- ✅ Check room availability by date range
- ✅ Book a room with customer information
- ✅ Make payment for booking
- ✅ View booking confirmation
- ✅ Admin login and dashboard
- ✅ Add/Edit/Delete rooms
- ✅ View and update booking statuses
- ✅ Add/Delete staff members

## Troubleshooting

**Database not found error**: 
- Make sure you run `python app.py` first to create the database
- The database file `hotel_booking.db` will be created automatically

**Port already in use**:
- Change the port in `app.py` (line 457): `app.run(debug=True, host='0.0.0.0', port=5001)`

**Module not found error**:
- Make sure you've installed all dependencies: `pip install -r requirements.txt`

