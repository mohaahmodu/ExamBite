from django.shortcuts import render

def register(request):
    return render(request, "register.html")

def login_view(request):
    return render(request, "login.html")