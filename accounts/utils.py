import random

def generate_otp():
    return str(random.randint(100000, 999999))


from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(user, otp):
    print(f"OTP for {user.email}: {otp}")