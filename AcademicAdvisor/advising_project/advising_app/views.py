import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET
from .forms import AddCompletedCourseForm, EditCompletedCourseForm, EditCurrentCoursesForm, MessageForm, StudentProfileForm, StudyPlanEntryForm, StudyPlanForm, TutorProfileForm, YearlyStructureForm
from .models import Course, CustomUser, Major, Message, School,StudentCourseHistory, StudentProfile, StudyPlan, StudyPlanEntry, TutorAssignment, CurrentCourse, TutorProfile
from django.db.models import Q
from django.core.paginator import Paginator
from appointment_booking.models import Appointment, TimeSlot

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Determine the user's role and redirect accordingly
            if user.is_student:
                return redirect('student_dashboard_view')
            elif user.is_tutor:
                return redirect('tutor_dashboard_view')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout


@login_required
def student_dashboard_view(request):
    student = request.user
    profile, created = StudentProfile.objects.get_or_create(user=student)
    form = StudentProfileForm(instance=profile)
    current_year = datetime.datetime.now().year
    yearly_structure_form = YearlyStructureForm()
    structured_courses = None
    remaining_courses = []
    progress_percentage = calculate_progress_percentage(request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = StudentProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('student_dashboard_view')

        if 'yearly_structure' in request.POST:
            yearly_structure_form = YearlyStructureForm(request.POST)
            if yearly_structure_form.is_valid():
                year = yearly_structure_form.cleaned_data['year']
                semester = yearly_structure_form.cleaned_data['semester']
                structured_courses = Course.objects.filter(
                    major=student.studentprofile.major,
                    year=year,
                    semester=semester
                )

    if not student.is_student:
        return HttpResponseRedirect('/') 

    student_profile = StudentProfile.objects.filter(user=student).first()

    current_courses = CurrentCourse.objects.filter(
        student=student,
        year=student_profile.study_year,
        semester=student_profile.selected_semester
        
    )

    course_history = StudentCourseHistory.objects.filter(student=student_profile.user)
    completed_courses = course_history.values_list('course', flat=True)

    remaining_courses = Course.objects.filter(
        major=student_profile.major
    ).exclude(id__in=completed_courses)


    tutor_assignment = TutorAssignment.objects.filter(student=student).first()
    tutor = tutor_assignment.tutor if tutor_assignment else None

    progress_percentage = calculate_progress_percentage(student)

    context = {
        'form': form,
        'student_name': student.get_full_name(),
        'student_profile': student_profile,
        'current_courses': current_courses,
        'completed_courses': completed_courses,
        'tutor': tutor,
        'current_year': current_year,
        'remaining_courses': remaining_courses,
        'progress_percentage': progress_percentage,
        'yearly_structure_form': yearly_structure_form,
        'structured_courses': structured_courses,
        'is_tutor_viewing': False,
    }

    return render(request, 'student_templates/student_dashboard.html', context)

# Tutor dashboard view with role-specific logic
@login_required
def tutor_dashboard_view(request):
    tutor_id = request.user.id
    tutor_name = request.user.get_full_name()
    assigned_students = TutorAssignment.objects.filter(tutor_id=tutor_id).select_related('student')
    tutor_profile, created = TutorProfile.objects.get_or_create(user_id=tutor_id)
    unread_messages_count = Message.objects.filter(recipient_id=tutor_id, read_at__isnull=True).count()
    
    # Fetching Appointments with Pending TimeSlots
    pending_appointments = Appointment.objects.filter(
        timeslot__tutor_id=tutor_id,
        timeslot__status=TimeSlot.PENDING
    ).select_related('timeslot', 'student').order_by('timeslot__start_time')

    context = {
        'tutor_name': tutor_name,
        'assigned_students': assigned_students,
        'unread_messages_count': unread_messages_count,
        'tutor_profile': tutor_profile,
        'contact_email': tutor_profile.contact_email,
        'pending_appointments': pending_appointments,  
    }

    return render(request, 'tutor_dashboard.html', context)



def programs_view(request):
    schools = School.objects.all()
    is_tutor = not request.user.is_student  

    return render(request, "programs.html", {
        'schools': schools,
        'is_tutor': is_tutor  
    })

def majors_view(request, school_id):
    school = School.objects.get(id=school_id)
    majors = Major.objects.filter(school=school)
    is_tutor = not request.user.is_student  

    return render(request, "majors.html", {
        'school': school, 
        'majors': majors,
        'is_tutor': is_tutor  
    })

def major_detail(request, major_id):
    major = get_object_or_404(Major, id=major_id)
    years = range(1, 5)  
    is_tutor = not request.user.is_student  
   
    courses_by_year_and_semester = {
        'semesterA': {},
        'semesterB': {},
    }

    for year in years:
        courses_by_year_and_semester['semesterA'][year] = major.courses.filter(semester="semesterA", year=year)
        courses_by_year_and_semester['semesterB'][year] = major.courses.filter(semester="semesterB", year=year)

    return render(request, "major_detail.html", {
        'major': major, 
        'courses_by_year_and_semester': courses_by_year_and_semester,
        'is_tutor': is_tutor  

    })


def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    is_tutor = not request.user.is_student  

    return render(request, 'course_detail.html', {
        'course': course,
        'is_tutor': is_tutor 

    })

def search(request):
    query = request.GET.get('q')
    year_filter = request.GET.get('year')
    semester_filter = request.GET.get('semester')
    credits_filter = request.GET.get('credits')
    is_tutor = not request.user.is_student  

    majors_query = Major.objects.all()
    if query:
        majors_query = majors_query.filter(Q(name__icontains=query) | Q(major_code__icontains=query))

    courses_query = Course.objects.all()
    if query:
        courses_query = courses_query.filter(Q(name__icontains=query) | Q(course_code__icontains=query))

    if year_filter:
        courses_query = courses_query.filter(year=year_filter)

    if semester_filter:
        courses_query = courses_query.filter(semester=semester_filter)

    if credits_filter:
        courses_query = courses_query.filter(course_credits=credits_filter)

    context = {
        'schools': School.objects.filter(name__icontains=query) if query else None,
        'majors': majors_query,
        'courses': courses_query,
        'query': query,
        'is_tutor': is_tutor  
    }

    return render(request, 'search_results.html', context)


def autocomplete(request):
    query = request.GET.get('term', '')  # 'term' is commonly used by jQuery UI Autocomplete
    schools = School.objects.filter(name__icontains=query)
    majors = Major.objects.filter(name__icontains=query)
    courses = Course.objects.filter(name__icontains=query) | Course.objects.filter(course_code__icontains=query)

    results = []
    for school in schools:
        results.append({'label': school.name, 'category': 'Schools'})
    for major in majors:
        results.append({'label': major.name, 'category': 'Majors'})
    for course in courses:
        results.append({'label': f'{course.name} ({course.course_code})', 'category': 'Courses'})

    return JsonResponse(results, safe=False)

@login_required
def update_tutor_profile(request):
    tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = TutorProfileForm(request.POST, instance=tutor_profile)
        if form.is_valid():
            form.save()
            return redirect('tutor_dashboard_view')  # Redirect to the tutor dashboard
    else:
        form = TutorProfileForm(instance=tutor_profile)

    
    return render(request, 'tutor_templates/update_tutor_profile.html', {'form': form})

@login_required
def tutor_profile_view(request, tutor_id):
    # Check if the logged-in user is a student
    if not request.user.is_student:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch the tutor's user instance and profile
    tutor = get_object_or_404(CustomUser, pk=tutor_id)
    tutor_profile = get_object_or_404(TutorProfile, user=tutor)

    # Render only the tutor's profile information in the template
    return render(request, 'tutor_profile_for_student.html', {
        'tutor': tutor,
        'tutor_profile': tutor_profile,
    })


@login_required
def update_student_profile(request):
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('student_dashboard_view')  
    else:
        form = StudentProfileForm(instance=student_profile)

    return render(request, 'update_profile.html', {'form': form})


def get_majors_for_school(request):
    school_id = request.GET.get('school_id')
    majors = Major.objects.filter(school_id=school_id).order_by('name')
    return JsonResponse(list(majors.values('id', 'name')), safe=False)



@login_required
def view_study_plan(request, student_id=None):
    # If a student_id is provided and the user is a tutor, view that student's plan
    if student_id and request.user.is_tutor:
        student = get_object_or_404(CustomUser, pk=student_id, is_student=True)
    else:
        # If no student_id or user is not a tutor, default to the logged-in user's plan
        student = request.user

    try:
        study_plan = StudyPlan.objects.get(user=student, year=timezone.now().year)
        entries = StudyPlanEntry.objects.filter(study_plan=study_plan).select_related('course')

        # Categorize entries by course type and year
        compulsory_courses_entries = [
            entry for entry in entries if entry.course.course_type in ['major', ''] and entry.course.year <= 2 and not (entry.course.year == 2 and entry.course.semester == 'semesterB')
        ]
        elective_courses_entries = [entry for entry in entries if entry.course.course_type == 'elective']
        national_requirement_courses_entries = [entry for entry in entries if entry.course.course_type == 'national_requirement']
        english_courses_entries = [entry for entry in entries if entry.course.course_type == 'english']
        major_courses_entries = [
            entry for entry in entries 
            if entry not in compulsory_courses_entries 
            and entry not in elective_courses_entries 
            and entry not in national_requirement_courses_entries 
            and entry not in english_courses_entries 
            or (entry.course.year == 2 and entry.course.semester == 'semesterB')
        ]

    except StudyPlan.DoesNotExist:
        study_plan = None
        compulsory_courses_entries = []
        elective_courses_entries = []
        national_requirement_courses_entries = []
        english_courses_entries = []
        major_courses_entries = []

    context = {
        'student': student,
        'study_plan': study_plan,
        'compulsory_courses_entries': compulsory_courses_entries,
        'elective_courses_entries': elective_courses_entries,
        'national_requirement_courses_entries': national_requirement_courses_entries,
        'english_courses_entries': english_courses_entries,
        'major_courses_entries': major_courses_entries,
    }

    return render(request, 'view_study_plan.html', context)



@login_required
def study_plan_view(request, student_id=None):
    student = request.user
    student_profile, created = StudentProfile.objects.get_or_create(user=student)
    if student_id and request.user.is_tutor:
        student = get_object_or_404(CustomUser, pk=student_id, is_student=True)
    else:
        student = request.user

    student_profile, created = StudentProfile.objects.get_or_create(user=student)
    
    # Fetch courses based on their types
    compulsory_courses = Course.objects.filter(
        major=student_profile.major,
        year__lte=2,
        semester__in=['semesterA', 'semesterB']
    ).exclude(year=2, semester='semesterB').prefetch_related('prerequisites')

    # Adjusted major courses query: Including courses from Year 2 Semester B onwards
    major_courses = Course.objects.filter(
        major=student_profile.major
    ).filter(
        Q(year__gt=2) | Q(year=2, semester='semesterB')
    )

    national_requirement_courses = Course.objects.filter(course_type='national_requirement')
    english_courses = Course.objects.filter(course_type='english')
    elective_courses = Course.objects.filter(course_type='elective')

    if request.method == 'POST':
        plan_year = request.POST.get('plan_year')
        if plan_year:
            try:
                plan_year = int(plan_year)  
                study_plan, created = StudyPlan.objects.get_or_create(
                    user=student,
                    year=plan_year
                )
                StudyPlanEntry.objects.filter(study_plan=study_plan).delete()  

                all_courses = list(compulsory_courses) + list(major_courses) + list(national_requirement_courses) + list(english_courses)
                for course in all_courses:
                    form_data = {
                        'course': course.id,
                        'grade': request.POST.get(f'grade_{course.id}'),
                        'year_taken': request.POST.get(f'year_{course.id}'),
                        'semester': request.POST.get(f'semester_{course.id}')
                    }
                    form = StudyPlanEntryForm(form_data)
                    if form.is_valid():
                        study_plan_entry = form.save(commit=False)
                        study_plan_entry.study_plan = study_plan
                        study_plan_entry.save()

                elective_course_ids = request.POST.getlist('elective_course_id[]')
                elective_grades = request.POST.getlist('elective_grade[]')
                elective_years = request.POST.getlist('elective_year[]')
                elective_semesters = request.POST.getlist('elective_semester[]')
                for idx, course_id in enumerate(elective_course_ids):
                    elective_form_data = {
                        'course': course_id,
                        'grade': elective_grades[idx],
                        'year_taken': elective_years[idx],
                        'semester': elective_semesters[idx]
                    }
                    elective_form = StudyPlanEntryForm(elective_form_data)
                    if elective_form.is_valid():
                        elective_entry = elective_form.save(commit=False)
                        elective_entry.study_plan = study_plan
                        elective_entry.save()

                messages.success(request, "Study plan saved successfully.")
                return redirect('view_study_plan')  # Redirect to the form with a success message
            except ValueError:
                messages.error(request, "Invalid year provided.")
                return redirect('study_plan')  # Redirect to the form with an error message
        else:
            messages.error(request, "Please provide a year for the study plan.")
            return redirect('study_plan')  # Redirect to the form with an error message
    else:
        # GET request handling to populate form with existing data
        try:
            study_plan = StudyPlan.objects.get(user=student, year=timezone.now().year)
            entries = StudyPlanEntry.objects.filter(study_plan=study_plan)
        except StudyPlan.DoesNotExist:
            study_plan = None
            entries = []

        saved_data = {entry.course.id: entry for entry in entries}
        context = {
            'compulsory_courses': compulsory_courses,
            'major_courses': major_courses,
            'national_requirement_courses': national_requirement_courses,
            'english_courses': english_courses,
            'current_year': timezone.now().year,
            'grade_choices': StudyPlanEntryForm.base_fields['grade'].choices,
            'semester_choices': StudyPlanEntryForm.base_fields['semester'].choices,
            'elective_courses': elective_courses,
            'saved_data': saved_data,
        }

        return render(request, 'study_plan.html', context)

@login_required
def tutor_students_list(request):
    if not request.user.is_authenticated or not request.user.is_tutor:
        return HttpResponseForbidden("You are not authorized to view this page.")

    search_query = request.GET.get('search_query', '')
    assigned_students = TutorAssignment.objects.filter(tutor=request.user)

    if search_query:
        assigned_students = assigned_students.filter(
            Q(student__id__icontains=search_query) | 
            Q(student__first_name__icontains=search_query) | 
            Q(student__last_name__icontains=search_query) | 
            Q(student__email__icontains=search_query)
        )

    return render(request, 'tutor_students_list.html', {'assigned_students': assigned_students})

@login_required
def tutor_student_dashboard_view(request, student_id):
    # Ensure that the logged-in user is a tutor.
    if not request.user.is_tutor:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch the student based on the primary key (id) only.
    student = get_object_or_404(CustomUser, pk=student_id)

    # Check if the fetched user is a student.
    if not student.is_student:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Check if the student is assigned to the logged-in tutor.
    if not TutorAssignment.objects.filter(tutor=request.user, student=student).exists():
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Proceed to fetch the student's profile and other details.
    student_profile = get_object_or_404(StudentProfile, user=student)

    # Get the student's current, completed, and remaining courses.
    current_courses = CurrentCourse.objects.filter(student=student)
    completed_courses = StudentCourseHistory.objects.filter(student=student)
    completed_course_ids = completed_courses.values_list('course', flat=True)
    tutor_assignment = TutorAssignment.objects.filter(student=student).first()
    tutor = tutor_assignment.tutor if tutor_assignment else None

    if student_profile.major:
        all_courses = Course.objects.filter(major=student_profile.major)
        remaining_courses = all_courses.exclude(id__in=completed_course_ids)

        # Calculate the progress based on completed credits.
        total_credits = all_courses.aggregate(Sum('course_credits'))['course_credits__sum'] or 0
        completed_credits = completed_courses.aggregate(Sum('course__course_credits'))['course__course_credits__sum'] or 0
        progress_percentage = (completed_credits / total_credits) * 100 if total_credits else 0
    else:
        remaining_courses = Course.objects.none()  # No remaining courses if no major is set.
        progress_percentage = 0

    yearly_structure_form = YearlyStructureForm()
    structured_courses = None

    if request.method == 'POST' and 'yearly_structure' in request.POST:
        yearly_structure_form = YearlyStructureForm(request.POST)
        if yearly_structure_form.is_valid():
            year = yearly_structure_form.cleaned_data['year']
            semester = yearly_structure_form.cleaned_data['semester']
            structured_courses = Course.objects.filter(
                major=student.studentprofile.major,
                year=year,
                semester=semester
            )
     # Fetch the remaining courses
    if student_profile.major:
        all_courses = Course.objects.filter(major=student_profile.major)
        completed_courses = StudentCourseHistory.objects.filter(student=student)
        completed_course_ids = completed_courses.values_list('course', flat=True)
        remaining_courses = all_courses.exclude(id__in=completed_course_ids)
    else:
        remaining_courses = Course.objects.none()
    # Prepare the context with the data we've gathered to pass to the template.
    context = {
        'student': student,
        'student_profile': student_profile,
        'current_courses': current_courses,
        'completed_courses': completed_courses,
        'remaining_courses': remaining_courses,
        'progress_percentage': progress_percentage,
        'tutor': tutor,
        'yearly_structure_form': yearly_structure_form,
        'structured_courses': structured_courses,
        'is_tutor_viewing': True,  
    }

    return render(request, 'student_templates/student_dashboard.html', context)


def student_dashboard(request):
    # Make sure the user is authenticated and is a student
    if not request.user.is_authenticated or not request.user.is_student:
        # Handle unauthenticated / non-student users
        return redirect('login')  # Redirect them to login or a proper error page

    # The logged-in user is the student
    student = request.user

    # Access the tutor directly from the student instance
    tutor = student.tutor

    context = {
        'student': student,
        'tutor': tutor,
    }

    return render(request, 'student_dashboard.html', context)

@login_required
def tutor_dashboard(request):
    if not request.user.is_tutor:
        return redirect('home')

    assigned_students = TutorAssignment.objects.filter(tutor=request.user)

    student_details = [
        {
            'student': assignment.student,
            'student_profile': assignment.student.studentprofile
        }
        for assignment in assigned_students
    ]

    context = {
        'assigned_students': assigned_students,
        'student_details': student_details,
    }

    return render(request, 'tutor_dashboard.html', context)

@login_required
def inbox(request):
    messages_per_page = 5

    messages_received_list = Message.objects.none()
    messages_sent_list = Message.objects.none()

    if request.user.is_student:
        messages_received_list = Message.objects.filter(recipient=request.user).order_by('-sent_at')
        messages_sent_list = Message.objects.filter(sender=request.user).order_by('-sent_at')

    elif request.user.is_tutor:
        students = request.user.students.all()
        messages_received_list = Message.objects.filter(recipient=request.user).order_by('-sent_at')
        messages_sent_list = Message.objects.filter(sender=request.user).order_by('-sent_at')
        messages_from_students = Message.objects.filter(sender__in=students).order_by('-sent_at')
        messages_received_list |= messages_from_students

    Message.objects.filter(recipient=request.user, read_at__isnull=True).update(read_at=timezone.now())

    received_page_number = request.GET.get('received_page', 1)
    received_paginator = Paginator(messages_received_list, messages_per_page)
    messages_received = received_paginator.get_page(received_page_number)

    sent_page_number = request.GET.get('sent_page', 1)
    sent_paginator = Paginator(messages_sent_list, messages_per_page)
    messages_sent = sent_paginator.get_page(sent_page_number)

    return render(request, 'inbox.html', {
        'messages_received': messages_received,
        'messages_sent': messages_sent,
        'messages': messages.get_messages(request)
    })


@login_required
def get_unread_messages_count(request):
    if not request.user.is_tutor:
        return JsonResponse({'count': 0})  

    count = Message.objects.filter(recipient=request.user, read_at__isnull=True).count()
    return JsonResponse({'count': count})

@login_required
def send_message(request):
    recipient_id = request.GET.get('recipient_id')
    initial_data = {}

    if request.user.is_student:
        initial_data['recipient'] = request.user.tutor
    elif request.user.is_tutor and recipient_id:
        recipient = get_object_or_404(CustomUser, pk=recipient_id)
        initial_data['recipient'] = recipient
    
    # If it's a POST request, we need to process the form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = MessageForm(request.POST, request.FILES)
        # Check if the form is valid:
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            message = form.save(commit=False)
            message.sender = request.user
            # Save the new instance.
            message.save()
            # Redirect to a new URL:
            messages.success(request, "Message has been sent successfully.")
            return redirect('inbox')
    # If it's a GET (or any other method), we'll create a blank form
    else:
        form = MessageForm(initial=initial_data)

    return render(request, 'send_message.html', {'form': form})

@login_required
def edit_current_courses(request):
    student = request.user
    student_profile, _ = StudentProfile.objects.get_or_create(user=student)

    if request.method == 'POST':
        form = EditCurrentCoursesForm(request.POST, major=student_profile.major)
        if form.is_valid():
            selected_required_courses = form.cleaned_data.get('required_courses')
            selected_elective_courses = form.cleaned_data.get('elective_courses')
            selected_courses = set(selected_required_courses) | set(selected_elective_courses)

            for course in selected_courses:
                CurrentCourse.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'semester': student_profile.selected_semester
                    }
                )

            messages.success(request, 'Courses added successfully.')
            return redirect('student_dashboard_view')
        else:
            messages.error(request, 'There was an error updating your courses.')
    else:
        form = EditCurrentCoursesForm(major=student_profile.major)

    current_courses = CurrentCourse.objects.filter(student=student)

    return render(request, 'edit_current_courses.html', {'form': form, 'current_courses': current_courses})

@login_required
def delete_current_course(request, course_id):
    course_to_delete = get_object_or_404(CurrentCourse, id=course_id, student=request.user)
    course_to_delete.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect('edit_current_courses')

@login_required
def add_completed_course(request):
    if request.method == 'POST':
        form = AddCompletedCourseForm(request.POST)
        if form.is_valid():
            completed_course = form.save(commit=False)
            completed_course.student = request.user
            completed_course.save()
            return redirect('completed_courses')
    else:
        form = AddCompletedCourseForm()
    return render(request, 'add_completed_courses.html', {'form': form})

@login_required
def edit_completed_course(request, pk):
    completed_course = get_object_or_404(StudentCourseHistory, pk=pk, student=request.user)
    if request.method == 'POST':
        form = EditCompletedCourseForm(request.POST, instance=completed_course)
        if form.is_valid():
            form.save()
            return redirect('completed_courses')
    else:
        form = EditCompletedCourseForm(instance=completed_course)
    return render(request, 'edit_completed_courses.html', {'form': form})

def completed_courses(request):
    student = request.user
    completed_courses = StudentCourseHistory.objects.filter(student=student).select_related('course')
    context = {
        'completed_courses': completed_courses,
        'is_tutor_viewing': False,  
    }
    return render(request, 'completed_courses.html', context)


from django.views.decorators.http import require_POST

from django.db.models import Sum
def calculate_progress_percentage(user):
    # Assuming this logic is already defined in student_dashboard_view, refactor it here
    student_profile = StudentProfile.objects.filter(user=user).first()
    if student_profile.major:
        completed_courses = StudentCourseHistory.objects.filter(student=student_profile.user).values_list('course', flat=True)
        required_courses = student_profile.major.courses.all()
        total_credits = required_courses.aggregate(Sum('course_credits'))['course_credits__sum'] or 0
        completed_credits = required_courses.filter(id__in=completed_courses).aggregate(Sum('course_credits'))['course_credits__sum'] or 0
        progress_percentage = (completed_credits / total_credits) * 100 if total_credits else 0
    else:
        progress_percentage = 0  # or other default value
    return progress_percentage

@login_required
@require_POST
def complete_course(request, course_id):
    course_id = request.POST.get('course_id')
    current_course = get_object_or_404(CurrentCourse, id=course_id, student=request.user)

    # Assuming default grade or handling it elsewhere. Adjust as necessary.
    default_grade = "N/A"

    # Create a new entry in StudentCourseHistory and delete the current course
    StudentCourseHistory.objects.create(
        student=request.user,
        course=current_course.course,
        year=current_course.year,
        grade=default_grade,
        custom_semester=current_course.semester,
        self_reported=False
    )
    current_course.delete()

    # Recalculate the progress percentage after deleting the course
    # Here you need to implement your own logic to calculate the new progress percentage
    new_progress_percentage = calculate_progress_percentage(request.user)

    return JsonResponse({'status': 'success', 'newProgressPercentage': new_progress_percentage})



@login_required
def remove_completed_course(request, pk):
    completed_course = get_object_or_404(StudentCourseHistory, pk=pk, student=request.user)
    if request.method == 'POST':
        completed_course.delete()
        return redirect('completed_courses')
    else:
        return redirect('completed_courses')


@login_required
def tutor_view_completed_courses(request, student_id):
    # Ensure the user is a tutor
    if not request.user.is_tutor:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Retrieve the specified student and their completed courses
    student = get_object_or_404(CustomUser, pk=student_id)
    completed_courses = StudentCourseHistory.objects.filter(student=student).select_related('course')

    context = {
        'completed_courses': completed_courses,
        'is_tutor_viewing': True,  
    }
    return render(request, 'completed_courses.html', context)

@login_required
def tutor_view_study_plan(request, student_id):
    # Fetch the student and ensure they are actually a student
    student = get_object_or_404(CustomUser, pk=student_id,)
    # Fetch the study plan for the student, if it exists
    study_plan = StudyPlan.objects.filter(user=student,year=timezone.now().year).first()
    compulsory_courses_entries = []
    elective_courses_entries = []

    if study_plan:
        entries = StudyPlanEntry.objects.filter(study_plan=study_plan).select_related('course')
        compulsory_courses_entries = [entry for entry in entries if entry.course.course_type == 'compulsory']
        elective_courses_entries = [entry for entry in entries if entry.course.course_type == 'elective']
        major_courses_entries = [entry for entry in entries if entry.course.course_type == 'major']

    context = {
        'student': student,
        'study_plan': study_plan,
        'compulsory_courses_entries': compulsory_courses_entries,
        'elective_courses_entries': elective_courses_entries,
        'major_courses_entries': major_courses_entries,
        'is_tutor_viewing': True,
    }
    return render(request, 'view_study_plan.html', context)

@login_required
def tutor_view_remaining_courses(request, student_id):
    # Ensure that the logged-in user is a tutor.
    if not request.user.is_tutor:
        return HttpResponseForbidden("You are not authorized to view this page.")
    # Check if the student is assigned to the logged-in tutor
    if not request.user.is_student_assigned(student_id):
        return HttpResponseForbidden("This student is not assigned to you.")
    student = get_object_or_404(CustomUser, pk=student_id)
    student_profile = StudentProfile.objects.get(user=student)
    major = student_profile.major

    if major:
        required_course_ids = list(major.courses.values_list('id', flat=True))
        completed_course_ids = list(StudentCourseHistory.objects.filter(student=student).values_list('course', flat=True))
        remaining_course_ids = set(required_course_ids) - set(completed_course_ids)
        remaining_courses = Course.objects.filter(id__in=remaining_course_ids)
    else:
        messages.info(request, "No major selected or no remaining courses.")
        remaining_courses = []

    context = {
        'remaining_courses': remaining_courses,
        'major': major,
        'student': student, 
    }

    return render(request, 'remaining_courses.html', context)



@login_required
def calculate_remaining_courses(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    major = student_profile.major

    if major:
        required_course_ids = list(major.courses.values_list('id', flat=True))
        completed_course_ids = list(StudentCourseHistory.objects.filter(
            student=request.user
        ).values_list('course', flat=True))
        remaining_course_ids = set(required_course_ids) - set(completed_course_ids)
        remaining_courses = Course.objects.filter(id__in=remaining_course_ids)
    else:
        messages.info(request, "You haven't chosen a major yet.")
        remaining_courses = []

    context = {
        'remaining_courses': remaining_courses,
        'major': major,
    }

    return render(request, 'remaining_courses.html', context)

@login_required
def get_completed_courses_data(request):
    student = request.user
    completed_courses = StudentCourseHistory.objects.filter(student=student).values(
        'course__name', 'year', 'grade', 'custom_semester'
    )
    return JsonResponse(list(completed_courses), safe=False)
