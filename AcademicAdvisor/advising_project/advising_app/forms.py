from django import forms
from .models import CurrentCourse, StudyPlan, StudyPlanEntry, StudentCourseHistory, CustomUser, Course, Message, StudentProfile, School, Major, TutorProfile
from django import forms
from django.utils import timezone
from django import forms
from .models import StudyPlanEntry
from django import forms
from .models import Meeting

class StudyPlanForm(forms.ModelForm):
    class Meta:
        model = StudyPlan
        fields = ['year']  

class StudyPlanEntryForm(forms.ModelForm):
    elective_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.filter(course_type='elective'), 
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        help_text='Select your elective courses'
    )

    grade = forms.ChoiceField(choices=[
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'), 
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'), 
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('F', 'F')
    ],
     required=False,
     )
    year_taken = forms.IntegerField(
        min_value=2020, 
        max_value=2100,
        required=False,  # Make this field optional
    )
    semester = forms.ChoiceField(choices=[
        ('semesterA', 'Semester A'), ('semesterB', 'Semester B')
    ],
     required=False,
     )

    class Meta:
        model = StudyPlanEntry
        fields = ['course', 'grade', 'year_taken', 'semester', 'elective_courses']




class AssignTutorForm(forms.Form):
    tutor = forms.ModelChoiceField(queryset=CustomUser.objects.filter(is_tutor=True))
    students = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.filter(is_student=True))


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['school', 'major', 'is_scholarship_student']

    def __init__(self, *args, **kwargs):
        super(StudentProfileForm, self).__init__(*args, **kwargs)
        if self.instance.school:
            self.fields['major'].queryset = Major.objects.filter(school=self.instance.school).order_by('name')
        else:
            self.fields['major'].queryset = Major.objects.none()

        self.fields['is_scholarship_student'].widget = forms.CheckboxInput(attrs={
            'class': 'custom-checkbox',
            'id': 'id_is_scholarship_student'
        })

from django.forms.widgets import TimeInput

class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ['location', 'contact_email', 'start_time', 'end_time']
        widgets = {
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super(TutorProfileForm, self).__init__(*args, **kwargs)
        self.fields['contact_email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.contact_email = self.cleaned_data['contact_email']
        if commit:
            profile.save()
        return profile
        
class EditCurrentCoursesForm(forms.ModelForm):
    semester = forms.ChoiceField(choices=Course.SEMESTER_CHOICES, required=True)
    
    # Required courses dropdown
    required_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.none(),  # This will be populated in the view
        widget=forms.SelectMultiple(attrs={'class': 'select2-required'}),
        required=False,
        label='Required Courses'
    )
    
    # Elective courses dropdown
    elective_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),  # All courses for electives
        widget=forms.SelectMultiple(attrs={'class': 'select2-electives'}),
        required=False,
        label='Elective Courses'
    )

    class Meta:
        model = CurrentCourse
        fields = [ 'semester', 'required_courses', 'elective_courses']

    def __init__(self, *args, **kwargs):
        major = kwargs.pop('major', None)  # Extract the major argument
        super(EditCurrentCoursesForm, self).__init__(*args, **kwargs)

        if major:
            self.fields['required_courses'].queryset = Course.objects.filter(major=major)
            self.fields['elective_courses'].queryset = Course.objects
        else:
            self.fields['required_courses'].queryset = Course.objects.none()
            self.fields['elective_courses'].queryset = Course.objects.none()
        # Retain the year and semester selections
        if 'year' in self.data:
            self.fields['year'].initial = self.data.get('year')
        if 'semester' in self.data:
            self.fields['semester'].initial = self.data.get('semester')
            self.data.get('semester')


class AddCompletedCourseForm(forms.ModelForm):
    class Meta:
        model = StudentCourseHistory
        fields = ['course', 'year', 'grade', 'custom_semester']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_semester': forms.Select(choices=Course.SEMESTER_CHOICES, attrs={'class': 'form-control'}),
        }

class EditCompletedCourseForm(forms.ModelForm):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('F', 'F')
    ]

    grade = forms.ChoiceField(choices=GRADE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.TypedChoiceField(coerce=int, choices=[(r, r) for r in range(2000, timezone.now().year+1)], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = StudentCourseHistory
        fields = ['course', 'year', 'grade', 'custom_semester']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'custom_semester': forms.Select(choices=Course.SEMESTER_CHOICES, attrs={'class': 'form-control'}),
        }

class CompletedCoursesForm(forms.ModelForm):
    class Meta:
        model = StudentCourseHistory
        fields = ['course', 'year', 'grade', 'custom_semester']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_semester': forms.Select(attrs={'class': 'form-control'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body', 'file']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class YearlyStructureForm(forms.Form):
    YEAR_CHOICES = [(i, f"Year {i}") for i in range(1, 5)]  # Assuming 4 years
    SEMESTER_CHOICES = [
        ('semesterA', 'Semester A'),
        ('semesterB', 'Semester B'),
    ]

    year = forms.ChoiceField(choices=YEAR_CHOICES, label='Year')
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, label='Semester')


class BookingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['meeting_date', 'start_time', 'end_time', 'student', 'tutor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, set the queryset for student and tutor fields based on the user's role
