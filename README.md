# Hotel Booking System

A comprehensive hotel booking management system built with Flask and SQLite. This system allows users to book rooms, check availability, and make payments. Administrators can manage room inventory, reservations, and staff.

## Features

### User Features
- **Browse Rooms**: View all available rooms with details
- **Check Availability**: Search for available rooms by date range
- **Book Rooms**: Make reservations with customer information
- **Make Payments**: Complete payment for bookings
- **Booking Confirmation**: Receive confirmation with booking details

### Admin Features
- **Dashboard**: View statistics and recent bookings
- **Room Management**: Add, edit, and delete rooms
- **Booking Management**: View and update booking statuses
- **Staff Management**: Add and manage staff members
- **Payment Tracking**: Monitor payments and revenue

## Database Schema

The system uses the following main tables:

- **rooms**: Room information (number, type, price, capacity, amenities, status)
- **customers**: Customer details (name, email, phone, address)
- **bookings**: Reservation records (dates, guests, amount, status)
- **payments**: Payment transactions (method, amount, status, transaction ID)
- **staff**: Staff members (name, role, credentials)

## Installation

1. **Clone or download the project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   The database will be automatically created when you first run the application.

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   - Open your browser and navigate to: `http://localhost:5000`
   - For admin access, use the login page: `http://localhost:5000/login`

## Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Important**: Change the default admin password after first login in a production environment!

## Project Structure

```
DBMS/
├── app.py                 # Main Flask application
├── database.py            # Database helper functions
├── schema.sql             # Database schema
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── book.html
│   ├── payment.html
│   ├── confirmation.html
│   └── admin/
│       ├── dashboard.html
│       ├── rooms.html
│       ├── add_room.html
│       ├── edit_room.html
│       ├── bookings.html
│       ├── staff.html
│       └── add_staff.html
└── static/                # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Usage Guide

### For Users

1. **Browse Rooms**: Visit the home page to see all available rooms
2. **Check Availability**: 
   - Enter check-in and check-out dates
   - Click "Check Availability" to see available rooms for those dates
3. **Book a Room**:
   - Click "Book Now" on any room
   - Fill in customer information and booking details
   - Complete the payment process
4. **View Confirmation**: After payment, view your booking confirmation

### For Administrators

1. **Login**: Use admin credentials to access the admin panel
2. **Manage Rooms**:
   - Add new rooms with details (number, type, price, capacity)
   - Edit existing room information
   - Delete rooms (if no active bookings)
3. **Manage Bookings**:
   - View all bookings
   - Update booking status (pending, confirmed, checked-in, checked-out, cancelled)
4. **Manage Staff**:
   - Add new staff members with roles (admin, manager, receptionist, housekeeping)
   - Delete staff members

## Room Statuses

- **available**: Room is ready for booking
- **occupied**: Room is currently occupied
- **maintenance**: Room is under maintenance and unavailable

## Booking Statuses

- **pending**: Booking created but payment not completed
- **confirmed**: Payment completed, booking confirmed
- **checked_in**: Guest has checked in
- **checked_out**: Guest has checked out
- **cancelled**: Booking has been cancelled

## Payment Methods

- Credit Card
- Debit Card
- Online Transfer
- Cash (Pay at Hotel)

## Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with modern design

## Security Notes

- Passwords are hashed using SHA256 (consider using bcrypt for production)
- Session management for admin authentication
- SQL injection protection through parameterized queries
- Input validation on forms

## Future Enhancements

- Email notifications for bookings
- Advanced search and filtering
- Room images and galleries
- Customer account management
- Booking cancellation with refunds
- Reports and analytics
- Multi-language support
- Mobile app integration

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please check the code comments or create an issue in the repository.

