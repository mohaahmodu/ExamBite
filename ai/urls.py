from django.urls import path
from .views import test_ai

urlpatterns = [
    path("test/", test_ai, name="test_ai"),
]