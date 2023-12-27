from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
import csv
from .models import (
    School, Major, Course, CustomUser, Meeting,
    StudentProfile, TutorAssignment, StudentCourseHistory, TutorProfile
)
from .forms import AssignTutorForm


admin.site.register(School)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'semester', 'course_type']
    search_fields = ['name', 'course_code', 'course_description']
admin.site.register(TutorAssignment)


# Function to export student course history
def export_student_course_history(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_course_history.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Email', 'Course Name', 'Year', 'Grade', 'Semester'])
    
    for student in queryset:
        course_histories = StudentCourseHistory.objects.filter(student=student)
        for history in course_histories:
            writer.writerow([student.email, history.course.name, history.year, history.grade, history.custom_semester])
    
    return response
export_student_course_history.short_description = "Export Student Course History"

# Admin for Major with filter_horizontal 
@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['name', 'major_code', 'school']
    search_fields = ['name', 'major_code', 'description']
    filter_horizontal = ('courses',)

# Inline for StudentCourseHistory
class StudentCourseHistoryInline(admin.TabularInline):
    model = StudentCourseHistory
    extra = 0

# Admin for CustomUser with the new export action
from django.contrib import admin
from django.contrib.admin import SimpleListFilter

class UserRoleFilter(SimpleListFilter):
    title = 'user role'  # or use _('user role') for i18n
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return (
            ('student', 'Student'),
            ('tutor', 'Tutor'),
            ('admin', 'Admin'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'student':
            return queryset.filter(is_student=True)
        elif self.value() == 'tutor':
            return queryset.filter(is_tutor=True)
        elif self.value() == 'admin':
            return queryset.filter(is_admin=True)

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'student profiles'
    fk_name = 'user'
    fields = ('major', 'school',) 


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email_link', 'first_name', 'last_name', 'is_student', 'is_tutor']
    list_filter = (UserRoleFilter,)
    search_fields = ['first_name', 'last_name']
    inlines = [StudentCourseHistoryInline,StudentProfileInline]
    actions = [export_student_course_history, 'assign_students_to_tutor']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password1', 'password2', 'first_name', 'last_name', 'is_student', 'is_tutor'),
        }),
    )

    def email_link(self, obj):
        link = reverse("admin:advising_app_customuser_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', link, obj.email)
    email_link.short_description = 'Email'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('assign-tutor/', self.admin_site.admin_view(self.assign_tutor_view), name='assign-tutor'),
        ]
        return custom_urls + urls
    
    def assign_students_to_tutor(self, request, queryset):
        selected_students = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return render(request, 'admin/assign_tutor.html', {'students': selected_students})

    def assign_tutor_view(self, request):
        if request.method == 'POST':
            form = AssignTutorForm(request.POST)
            if form.is_valid():
                tutor = form.cleaned_data['tutor']
                students = form.cleaned_data['students']
                for student_id in students:
                    student = CustomUser.objects.get(pk=student_id)
                    TutorAssignment.objects.create(student=student, tutor=tutor)
                self.message_user(request, "Tutor assigned successfully.")
                return HttpResponseRedirect(reverse('admin:index'))
        else:   
            form = AssignTutorForm()
        return render(request, 'admin/assign_tutor.html', {'form': form})