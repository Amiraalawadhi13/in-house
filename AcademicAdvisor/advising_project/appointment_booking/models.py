from django.db import models
from django.conf import settings


class TimeSlot(models.Model):
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    PENDING = 'pending'
    DONE = 'done'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (DONE, 'Done'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.tutor} - {self.start_time} to {self.end_time}"

    def book(self):
        self.is_booked = True
        self.save()

    def unbook(self):
        self.is_booked = False
        self.save()

class Appointment(models.Model):
    timeslot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment with {self.timeslot.tutor} for {self.student} on {self.timeslot.start_time}"

