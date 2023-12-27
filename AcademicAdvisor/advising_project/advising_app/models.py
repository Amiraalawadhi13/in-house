from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    SEMESTER_CHOICES = [
        ("semesterA", "semester A"),
        ("semesterB", "semester B"),
    ]
    COURSE_TYPE_CHOICES = [
        ('elective', 'Elective Course'),
        ('national_requirement', 'National Requirement'),
        ('english', 'English Course'),
        ('compulsory', 'Compulsory Course'),         
        ('major_specific', 'Major Specific Course')  
    ]

    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField(null=True, blank=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, null=True)
    course_credits = models.IntegerField(null=True)
    course_code = models.CharField(max_length=20, null=True)
    course_description = models.TextField(null=True)
    nqf_lvl = models.IntegerField(null=True)
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True, related_name='postrequisites')
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, null=True, blank=True, default='major')

    def __str__(self):
        return self.name

class Major(models.Model):
    name = models.CharField(max_length=100)
    major_credit = models.IntegerField(null=True)
    major_code = models.CharField(max_length=20, null=True)
    description = models.TextField(null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return self.name
      

class Meeting(models.Model):
    meeting_date = models.DateField()
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='student_meetings')
    tutor = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='tutor_meetings')
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending')
    notes = models.TextField(blank=True, null=True)  # Optional field for any notes about the meeting
    
    def __str__(self):
        return f"Meeting on {self.meeting_date}"

from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to='message_files/', null=True, blank=True)  
    
    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}: {self.subject}"
    
    def mark_as_read(self):
        if self.read_at is None:
            self.read_at = timezone.now()
            self.save()

class TutorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_profile')
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(max_length=255)
    working_hours = models.CharField(max_length=255, blank=True, null=True) #removwe this
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

class StudentProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    program = models.CharField(max_length=100, null=True)
    study_year = models.PositiveIntegerField(null=True)
    selected_semester = models.CharField(max_length=20, default='semesterA')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, blank=True)
    is_scholarship_student = models.BooleanField(default=False, verbose_name="Scholarship Student")

    def __str__(self):
        return f"Profile of {self.user}"

class StudentCourseHistory(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)  
    year = models.PositiveIntegerField()
    grade = models.CharField(max_length=2)
    custom_semester = models.CharField(max_length=20)
    self_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.grade}"

#StudentProfile model to define the relationship with StudentCourseHistory
StudentProfile.courses_taken = models.ManyToManyField(Course, through=StudentCourseHistory)

class CurrentCourse(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='current_courses')
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=20)  

    def __str__(self):
        return f"{self.student} - {self.course}"
StudentProfile.courses_taken = models.ManyToManyField(Course, through=CurrentCourse)
    

class TutorAssignment(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='assigned_students')
    tutor = models.ForeignKey('CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tutor} assigned to {self.student}"

class StudyPlan(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='study_plans')
    year = models.PositiveIntegerField()  # Add this if 'year' is a property of StudyPlan

    def __str__(self):
        return f"{self.user.get_full_name()}'s Study Plan for {self.year}"  # Updated to include year


class StudyPlanEntry(models.Model):
    study_plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_taken = models.PositiveIntegerField()
    semester = models.CharField(max_length=10, choices=Course.SEMESTER_CHOICES)
    grade = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f"{self.course.name} - Year {self.year_taken} {self.semester}"


class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False) #deelete this
    is_admin = models.BooleanField(default=False)

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    tutor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_assigned_tutor(self):
        if hasattr(self, 'tutor'):
          return self.tutor
        return None
    
    def is_student_assigned(self, student_id):
        # This method checks if a student is assigned to the current tutor user
        return self.students.filter(id=student_id).exists()

    def __str__(self):
        return self.email

