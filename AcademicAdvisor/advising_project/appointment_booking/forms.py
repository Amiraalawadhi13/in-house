from django import forms
from django.core.exceptions import ValidationError
from .models import TimeSlot

class TimeSlotForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.tutor = kwargs.pop('tutor', None)
        super(TimeSlotForm, self).__init__(*args, **kwargs)

        # Adding custom attributes to form fields
        self.fields['start_time'].widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',  
                'placeholder': 'Select start time'
            }
        )
        self.fields['end_time'].widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',  
                'placeholder': 'Select end time'
            }
        )

    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # Check if start_time is before end_time
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time.")

        # Check for overlapping slots
        if start_time and end_time and self.tutor:
            overlapping_slots = TimeSlot.objects.filter(
                tutor=self.tutor,
                start_time__lt=end_time, 
                end_time__gt=start_time
            ).exclude(id=getattr(self.instance, 'id', None))

            if overlapping_slots.exists():
                raise ValidationError("This time slot overlaps with an existing one for this tutor.")

        return cleaned_data

