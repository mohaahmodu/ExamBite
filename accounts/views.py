from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .models import OTP
from .utils import generate_otp, send_otp_email
from django.contrib.auth.models import User
from django.contrib import messages

import requests

from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Subscription


def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        institution = request.POST.get("institution")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate required fields
        if not all([full_name, username, email, password, confirm_password]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("register")

        # Confirm passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Check username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        # Check email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        # Create inactive user
        user = User.objects.create_user(
            username=username,
            first_name=full_name,
            email=email,
            password=password,
            is_active=False
        )

        # Generate OTP
        code = generate_otp()

        # Save OTP
        OTP.objects.create(
            user=user,
            code=code
        )

        # Send OTP email
        send_otp_email(user, code)

        # Store user ID in session
        request.session["user_id"] = user.id

        messages.success(request, "An OTP has been sent to your email.")

        return redirect("verify_otp")

    return render(request, "register.html")

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        login_input = request.POST.get("username")  # username or email
        password = request.POST.get("password")

        # Check if the input is an email
        if "@" in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = login_input
        else:
            username = login_input

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        # Better error messages
        try:
            user_obj = User.objects.get(username=username)

            if not user_obj.is_active:
                messages.error(request, "Please verify your email before logging in.")
            else:
                messages.error(request, "Invalid username/email or password.")

        except User.DoesNotExist:
            messages.error(request, "Invalid username/email or password.")

    return render(request, "login.html")


from django.shortcuts import get_object_or_404
from django.contrib.auth import login

def verify_otp(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        code = request.POST["otp"]

        try:
            otp = OTP.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest("created_at")

            if otp.is_expired():
                messages.error(request, "OTP has expired.")
                return redirect("verify_otp")

            otp.is_used = True
            otp.save()

            user.is_active = True
            user.save()

            login(request, user)

            request.session.pop("user_id", None)

            return redirect("dashboard")

        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP.")

    return render(request, "verify_otp.html")

from django.contrib.auth.models import User

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            # Delete old OTPs
            OTP.objects.filter(user=user, is_used=False).delete()

            # Generate new OTP
            code = generate_otp()

            OTP.objects.create(
                user=user,
                code=code
            )

            send_otp_email(user, code)

            request.session["reset_user_id"] = user.id

            messages.success(request, "A password reset OTP has been sent to your email.")

            return redirect("verify_reset_otp")

        except User.DoesNotExist:
            messages.error(request, "No account exists with this email.")

    return render(request, "forgot_password.html")

def verify_reset_otp(request):
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        code = request.POST.get("otp")

        try:
            otp = OTP.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest("created_at")

            if otp.is_expired():
                messages.error(request, "OTP has expired.")
                return redirect("verify_reset_otp")

            otp.is_used = True
            otp.save()

            return redirect("reset_password")

        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP.")

    return render(request, "verify_reset_otp.html")


def reset_password(request):
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user.set_password(password)
        user.save()

        request.session.pop("reset_user_id", None)

        messages.success(request, "Password changed successfully. Please login.")

        return redirect("login")

    return render(request, "reset_password.html")

@login_required
def subscribe(request):

    return render(
        request,
        "accounts/subscribe.html",
        {
            "public_key": settings.PAYSTACK_PUBLIC_KEY,
            "amount": 600,
        }
    )


@login_required
def initialize_payment(request):

    callback_url = request.build_absolute_uri(
        reverse("payment_callback")
    )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": request.user.email,
        "amount": 60000,   # ₦600 in kobo
        "callback_url": callback_url,
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=payload,
        headers=headers,
    )

    data = response.json()

    if data.get("status"):

        return redirect(
            data["data"]["authorization_url"]
        )

    return redirect("subscribe")


@login_required
def payment_callback(request):

    from datetime import timedelta

    reference = request.GET.get("reference")

    if not reference:

        messages.error(
            request,
            "Invalid payment reference."
        )

        return redirect("subscribe")


    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }


    try:

        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers,
            timeout=30
        )

        result = response.json()

    except Exception:

        messages.error(
            request,
            "Unable to verify payment. Please try again."
        )

        return redirect("subscribe")


    if (
        result.get("status")
        and result.get("data", {}).get("status") == "success"
    ):

        subscription, created = Subscription.objects.get_or_create(
            user=request.user
        )

        subscription.is_active = True

        subscription.amount = 600

        subscription.paystack_reference = reference

        subscription.start_date = timezone.now()

        subscription.expiry_date = (
            timezone.now() + timedelta(days=30)
        )

        subscription.save()


        messages.success(
            request,
            "🎉 Payment successful! Your Premium subscription is now active for 30 days."
        )

        return redirect("notes")


    messages.error(
        request,
        "Payment verification failed. If you were charged, please contact support."
    )

    return redirect("subscribe")