from email.mime.text import MIMEText
import smtplib
from django.contrib import messages
from django.urls import reverse
from .models import TimeSlot, Appointment
from .forms import TimeSlotForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from advising_app.models import TutorAssignment  
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from .models import TimeSlot
from appointment_booking.models import TimeSlot
from django.core.paginator import Paginator
from email.message import EmailMessage
from django.conf import settings

@login_required
def time_slot_list(request):
    if request.method == 'POST':
        form = TimeSlotForm(request.POST, tutor=request.user)
        if form.is_valid():
            new_timeslot = form.save(commit=False)
            new_timeslot.tutor = request.user
            new_timeslot.save()
            return redirect('appointment_booking:time_slot_list')
    else:
        form = TimeSlotForm()

    timeslots_list = TimeSlot.objects.filter(tutor=request.user)
    paginator = Paginator(timeslots_list, 5)  
    page_number = request.GET.get('page')
    timeslots = paginator.get_page(page_number)

    # Fetching assigned students and their meeting counts
    assigned_students = TutorAssignment.objects.filter(tutor=request.user)
    student_meeting_counts = {
        assignment.student: TimeSlot.objects.filter(
            tutor=request.user,
            appointment__student=assignment.student,
            is_booked=True,
            status='done'  
        ).count()
        for assignment in assigned_students
    }

    return render(request, 'appointment_booking/timeslots.html', {
        'timeslots': timeslots,
        'form': form,
        'student_meeting_counts': student_meeting_counts
    })



@login_required
def delete_time_slot(request, slot_id):
    timeslot = get_object_or_404(TimeSlot, id=slot_id, tutor=request.user)  # Ensure that only the tutor can delete
    if request.method == 'POST':
        timeslot.delete()
        return redirect('appointment_booking:time_slot_list')
    return render(request, 'appointment_booking/confirm_delete.html', {'timeslot': timeslot})


@login_required
def student_tutor_timeslots_view(request):
    student = request.user
    booked_appointments = []
    if student.is_student:  
        try:
            tutor_assignment = TutorAssignment.objects.get(student=student)
            all_tutor_timeslots = TimeSlot.objects.filter(tutor=tutor_assignment.tutor)
            
            # Get booked appointments for the current student and the assigned tutor
            booked_appointments = Appointment.objects.filter(student=student, timeslot__in=all_tutor_timeslots)
            
            # Filter not booked timeslots
            timeslots = [timeslot for timeslot in all_tutor_timeslots if not timeslot.is_booked]
            
        except TutorAssignment.DoesNotExist:
            timeslots = []
            messages.error(request, "No assigned tutor.")
    else:
        timeslots = []
        messages.error(request, "Access restricted to students.")

    return render(request, 'appointment_booking/student_tutor_timeslots.html', {
        'timeslots': timeslots, 
        'booked_appointments': booked_appointments
    })

@login_required
def book_timeslot(request, timeslot_id):
    timeslot = TimeSlot.objects.filter(id=timeslot_id).first()
    timeslot.is_booked = True
    timeslot.save()
    
    Appointment.objects.create(
        timeslot=timeslot, 
        student=request.user,
    )
    message = EmailMessage();

    message['Subject'] = "Appointment confirmation" 
    message['From'] = settings.EMAIL_HOST_USER  
    message['To'] = request.user.email,
    message.set_content(  'Dear Sutdent,\n\nAppointment booked !!\n\nYour appointment with your academic advisor has been booked.\n\nStart: ' + timeslot.start_time.strftime('%a %d %b %Y, %I:%M%p') +'\n\nEnd:'+timeslot.end_time.strftime('%a %d %b %Y, %I:%M%p')+'\n\nkind regards,\nBooking system');  
    
    with smtplib.SMTP(settings.EMAIL_HOST, 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.ehlo()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, initial_response_ok=True) 
        server.ehlo()
        server.sendmail(settings.EMAIL_HOST_USER, request.user.email,message.as_string())
        print('Email sent!')
        server.close();
    messages.success(request, "Appointment booked successfully.")

    return redirect('appointment_booking:student_tutor_timeslots')

@login_required
def mark_timeslot_as_done(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id, tutor=request.user)
    timeslot.status = TimeSlot.DONE
    timeslot.save()
    return redirect('appointment_booking:time_slot_list')