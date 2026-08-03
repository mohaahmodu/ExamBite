from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    FILE_TYPES = [
        ("pdf", "PDF"),
        ("docx", "DOCX"),
        ("txt", "TXT"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    title = models.CharField(max_length=255)

    file = models.FileField(upload_to="notes/")

    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPES
    )

    # AI Generated Content
    summary = models.TextField(blank=True, null=True)

    flashcards = models.TextField(blank=True, null=True)

    cbt_questions = models.TextField(blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ("mcq", "Multiple Choice"),
        ("theory", "Theory"),
        ("short", "Short Answer"),
        ("mixed", "Mixed"),
    ]

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()
    answer = models.TextField()

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]

class Flashcard(models.Model):

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="ai_flashcards"
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.question[:50]

class TrueFalseQuestion(models.Model):

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="true_false_questions"
    )

    statement = models.TextField()

    answer = models.BooleanField()

    explanation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.statement[:50]
        