from django.http import HttpResponse
from .ai_service import ask_ai


def test_ai(request):
    prompt = "Explain database systems in simple terms."

    answer = ask_ai(prompt)

    return HttpResponse(answer)