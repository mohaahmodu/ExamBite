from django.urls import path
from . import views


urlpatterns = [

    path("", views.notes_dashboard, name="notes"),

    path(
        "upload/",
        views.upload_note,
        name="upload_note"
    ),

    path(
        "summary/<int:note_id>/",
        views.generate_summary,
        name="generate_summary"
    ),

    path(
        "summary/view/<int:note_id>/",
        views.view_summary,
        name="view_summary"
    ),


    path(
    "cbt/setup/<int:note_id>/",
    views.generate_cbt,
    name="generate_cbt"
    ),


    path(
        "delete/<int:note_id>/",
        views.delete_note,
        name="delete_note"
    ),


    path(
        "flashcards/generate/<int:note_id>/",
        views.generate_flashcards,
        name="generate_flashcards"
    ),


    path(
        "flashcards/<int:note_id>/",
        views.view_flashcards,
        name="view_flashcards"
    ),


    path(
        "flashcards/setup/<int:note_id>/",
        views.flashcard_setup,
        name="flashcard_setup"
    ),


    # CBT SYSTEM

    path(
        "cbt/setup/<int:note_id>/",
        views.generate_cbt,
        name="generate_cbt"
    ),

    path(
        "cbt/<int:note_id>/",
        views.view_cbt,
        name="view_cbt"
    ),

]