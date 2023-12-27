from django.contrib import admin
from .models import TimeSlot, Appointment  

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'start_time', 'end_time', 'is_booked', 'status')
    list_filter = ('is_booked', 'status', 'tutor')
    search_fields = ('tutor__username',)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('timeslot', 'student', 'created_at')
    list_filter = ('student',)
    search_fields = ('student__username', 'timeslot__tutor__username')

admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Appointment, AppointmentAdmin)
