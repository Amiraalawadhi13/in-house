// static/js/calendar-setup.js

document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        // FullCalendar configuration options
        // ...
    });

    calendar.render();
});

function showModal(modalId) {
    // Code to show your modal
    var modal = document.getElementById(modalId);
    modal.style.display = "block";
}
