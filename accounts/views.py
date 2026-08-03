from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from .models import OTP
from .utils import generate_otp, send_otp_email


def register(request):
    if request.method == "POST":

        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        institution = request.POST.get("institution")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not all([full_name, username, email, password, confirm_password]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            first_name=full_name,
            email=email,
            password=password,
            is_active=False
        )

        code = generate_otp()

        OTP.objects.create(
            user=user,
            code=code
        )

        send_otp_email(user, code)

        request.session["user_id"] = user.id

        messages.success(
            request,
            "An OTP has been sent to your email."
        )

        return redirect("verify_otp")

    return render(request, "register.html")



def login_view(request):

    if request.method == "POST":

        login_input = request.POST.get("username")
        password = request.POST.get("password")

        username = login_input

        if "@" in login_input:

            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username

            except User.DoesNotExist:
                pass


        user = authenticate(
            request,
            username=username,
            password=password
        )


        if user:

            login(request, user)

            return redirect("dashboard")


        messages.error(
            request,
            "Invalid username/email or password."
        )


    return render(request, "login.html")



def logout_view(request):

    logout(request)

    return redirect("login")



def verify_otp(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register")


    user = get_object_or_404(
        User,
        id=user_id
    )


    if request.method == "POST":

        code = request.POST.get("otp")


        try:

            otp = OTP.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest("created_at")


            if otp.is_expired():

                messages.error(
                    request,
                    "OTP has expired."
                )

                return redirect("verify_otp")


            otp.is_used = True
            otp.save()


            user.is_active = True
            user.save()


            login(request, user)

            request.session.pop(
                "user_id",
                None
            )


            return redirect("dashboard")


        except OTP.DoesNotExist:

            messages.error(
                request,
                "Invalid OTP."
            )


    return render(
        request,
        "verify_otp.html"
    )



def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")


        try:

            user = User.objects.get(
                email=email
            )


            OTP.objects.filter(
                user=user,
                is_used=False
            ).delete()


            code = generate_otp()


            OTP.objects.create(
                user=user,
                code=code
            )


            send_otp_email(
                user,
                code
            )


            request.session["reset_user_id"] = user.id


            messages.success(
                request,
                "Password reset OTP sent."
            )


            return redirect(
                "verify_reset_otp"
            )


        except User.DoesNotExist:

            messages.error(
                request,
                "No account exists with this email."
            )


    return render(
        request,
        "forgot_password.html"
    )



def verify_reset_otp(request):

    user_id = request.session.get(
        "reset_user_id"
    )


    if not user_id:
        return redirect(
            "forgot_password"
        )


    user = User.objects.get(
        id=user_id
    )


    if request.method == "POST":

        code = request.POST.get("otp")


        try:

            otp = OTP.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest("created_at")


            if otp.is_expired():

                messages.error(
                    request,
                    "OTP expired."
                )

                return redirect(
                    "verify_reset_otp"
                )


            otp.is_used = True
            otp.save()


            return redirect(
                "reset_password"
            )


        except OTP.DoesNotExist:

            messages.error(
                request,
                "Invalid OTP."
            )


    return render(
        request,
        "verify_reset_otp.html"
    )



def reset_password(request):

    user_id = request.session.get(
        "reset_user_id"
    )


    if not user_id:
        return redirect(
            "forgot_password"
        )


    user = User.objects.get(
        id=user_id
    )


    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")


        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "reset_password"
            )


        user.set_password(password)
        user.save()


        request.session.pop(
            "reset_user_id",
            None
        )


        messages.success(
            request,
            "Password changed successfully."
        )


        return redirect(
            "login"
        )


    return render(
        request,
        "reset_password.html"
    )