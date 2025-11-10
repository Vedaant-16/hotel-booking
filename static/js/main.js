// Main JavaScript file for Hotel Booking System

// Set minimum date to today for date inputs
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    const checkInInputs = document.querySelectorAll('input[type="date"][name="check_in"]');
    const checkOutInputs = document.querySelectorAll('input[type="date"][name="check_out"]');
    
    checkInInputs.forEach(input => {
        input.setAttribute('min', today);
    });
    
    checkOutInputs.forEach(input => {
        input.setAttribute('min', today);
    });
    
    // Update check-out minimum date when check-in date changes
    checkInInputs.forEach(checkIn => {
        checkIn.addEventListener('change', function() {
            const checkInDate = this.value;
            checkOutInputs.forEach(checkOut => {
                if (checkOut.closest('form') === checkIn.closest('form')) {
                    checkOut.setAttribute('min', checkInDate);
                    if (checkOut.value && checkOut.value <= checkInDate) {
                        checkOut.value = '';
                    }
                }
            });
        });
    });
});

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

