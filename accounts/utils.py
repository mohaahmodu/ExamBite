import random

def generate_otp():
    return str(random.randint(100000, 999999))


from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(user, otp):
    send_mail(
        subject="Verify Your NACOS ExamBite Account",
        message=f"""
Hello {user.username},

Your verification code is:

{otp}

This code expires in 10 minutes.

If you didn't create an account, ignore this email.

NACOS ExamBite Team
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )