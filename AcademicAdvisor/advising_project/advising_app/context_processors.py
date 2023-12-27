from django.contrib.auth.decorators import login_required
from .models import Message

def unread_message_count_processor(request):
    if not request.user.is_authenticated:
        return {}
    
    unread_messages_count = 0
    if request.user.is_authenticated:
        unread_messages_count = Message.objects.filter(
            recipient=request.user, 
            read_at__isnull=True
        ).count()
    
    return {'unread_messages_count': unread_messages_count}

def user_roles(request):
    return {
        'is_tutor': request.user.groups.filter(name='Tutors').exists(),
        'is_student': request.user.groups.filter(name='Students').exists(),
    }