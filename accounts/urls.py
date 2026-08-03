from django.urls import path

from . import views


urlpatterns = [

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "verify-otp/",
        views.verify_otp,
        name="verify_otp"
    ),

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "verify-reset-otp/",
        views.verify_reset_otp,
        name="verify_reset_otp"
    ),

    path(
        "reset-password/",
        views.reset_password,
        name="reset_password"
    ),

    path(
        "subscribe/",
        views.subscribe,
        name="subscribe"
    ),

    path(
        "initialize-payment/",
        views.initialize_payment,
        name="initialize_payment"
    ),

    path(
        "payment/callback/",
        views.payment_callback,
        name="payment_callback"
    ),

]