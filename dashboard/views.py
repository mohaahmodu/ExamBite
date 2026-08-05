from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from notes.models import Note, Question, Flashcard


def home(request):
    return render(request, "home.html")


@login_required
def dashboard(request):

    user = request.user

    user_notes = Note.objects.filter(
        user=user
    )

    notes_count = user_notes.count()

    exams_count = Question.objects.filter(
        note__user=user
    ).count()

    flashcards_count = Flashcard.objects.filter(
        note__user=user
    ).count()


    recent_notes = user_notes[:5]


    context = {

        "notes_count": notes_count,

        "exams_count": exams_count,

        "flashcards_count": flashcards_count,

        "recent_notes": recent_notes,

    }


    return render(
        request,
        "dashboard/index.html",
        context
    )

