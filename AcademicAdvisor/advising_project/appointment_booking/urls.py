# appointment_booking/urls.py

from . import views
from django.urls import path, include


app_name = 'appointment_booking'

urlpatterns = [
    path('timeslots/', views.time_slot_list, name='time_slot_list'),  
        path('delete_time_slot/<int:slot_id>/', views.delete_time_slot, name='delete_time_slot'),
    path('student-tutor-timeslots/', views.student_tutor_timeslots_view, name='student_tutor_timeslots'),
    path('book_timeslot/<int:timeslot_id>/', views.book_timeslot, name='book_timeslot'),
    path('timeslots/<int:timeslot_id>/done/', views.mark_timeslot_as_done, name='mark_as_done'),

]
