import os
import json
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Note, Flashcard
from .file_reader import read_pdf, read_docx, read_txt
from .ai import ask_gemini

@login_required
def notes_dashboard(request):

    notes = Note.objects.filter(
        user=request.user
    )

    return render(
        request,
        "notes/index.html",
        {
            "notes": notes
        }
    )



@login_required
def upload_note(request):

    if request.method == "POST":

        title = request.POST.get("title")

        uploaded_file = request.FILES.get("file")


        if not uploaded_file:

            messages.error(
                request,
                "Please choose a file."
            )

            return redirect("upload_note")



        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower().replace(".", "")



        if extension not in [
            "pdf",
            "docx",
            "txt"
        ]:

            messages.error(
                request,
                "Only PDF, DOCX and TXT files are allowed."
            )

            return redirect("upload_note")



        Note.objects.create(
            user=request.user,
            title=title,
            file=uploaded_file,
            file_type=extension
        )



        messages.success(
            request,
            "Lecture note uploaded successfully."
        )


        return redirect("notes")



    return render(
        request,
        "notes/upload.html"
    )



@login_required
def generate_summary(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    if note.summary:

        return redirect(
            "view_summary",
            note.id
        )


    try:

        path = note.file.path


        if note.file_type == "pdf":

            text = read_pdf(path)

        elif note.file_type == "docx":

            text = read_docx(path)

        else:

            text = read_txt(path)



        if not text.strip():

            messages.error(
                request,
                "No readable text found."
            )

            return redirect("notes")



        text = text[:8000]



        prompt = f"""

You are a university lecturer.

Create a LONG and detailed study note from this lecture material.

Include:

- Topics and subtopics
- Definitions
- Important concepts
- Detailed explanations
- Examples
- Processes
- Important examination points


Do not make it short.

Write it as revision material for students preparing for CBT exams.


Lecture Material:

{text}

"""


        summary = ask_gemini(
            prompt
        )


        note.summary = summary

        note.save()



        messages.success(
            request,
            "Detailed summary generated successfully."
        )


        return redirect(
            "view_summary",
            note.id
        )


    except Exception as e:


        messages.error(
            request,
            f"Summary Error: {str(e)}"
        )


        return redirect("notes")

@login_required
def view_summary(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    return render(
        request,
        "notes/summary.html",
        {
            "note": note
        }
    )



@login_required
def generate_cbt(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    if request.method == "POST":


        amount = int(
            request.POST.get(
                "amount",
                10
            )
        )


        difficulty = request.POST.get(
            "difficulty",
            "medium"
        )


        allowed_amounts = [
            5,
            10,
            20,
            30
        ]


        if amount not in allowed_amounts:

            amount = 10



        source = note.summary or ""



        if not source:


            messages.error(
                request,
                "Please generate a summary first."
            )


            return redirect(
                "notes"
            )



        questions = []



        try:


            remaining = amount



            while remaining > 0:


                batch = min(
                    5,
                    remaining
                )



                prompt = f"""

You are a university lecturer creating a CBT exam.

Using ONLY the study note below.

Generate exactly {batch} multiple choice questions.

Difficulty:
{difficulty}


Return ONLY JSON.

Format:

[
{{
"question":"Question text",

"options":[
"Option A",
"Option B",
"Option C",
"Option D"
],

"answer":"Correct option",

"explanation":"Short explanation"
}}
]


Rules:

- Exactly {batch} questions.
- Exactly four options.
- One correct answer only.
- No markdown.
- No extra text.
- Keep explanations short.


Study Note:

{source}

"""


                response = ask_gemini(
                    prompt
                )



                response = response.replace(
                    "```json",
                    ""
                )

                response = response.replace(
                    "```",
                    ""
                ).strip()



                match = re.search(
                    r"\[.*\]",
                    response,
                    re.DOTALL
                )



                if not match:

                    raise Exception(
                        "Invalid AI response"
                    )



                batch_questions = json.loads(
                    match.group(0)
                )



                questions.extend(
                    batch_questions
                )



                remaining -= len(
                    batch_questions
                )



            questions = questions[:amount]



            if not questions:

                raise Exception(
                    "No questions generated"
                )



            return render(
                request,
                "notes/cbt_exam.html",
                {
                    "note": note,
                    "questions": questions
                }
            )



        except Exception as e:


            messages.error(
                request,
                f"CBT Error: {str(e)}"
            )


            return redirect(
                "notes"
            )



    return render(
        request,
        "notes/cbt_setup.html",
        {
            "note": note
        }
    )



@login_required
def view_cbt(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    return render(
        request,
        "notes/cbt_exam.html",
        {
            "note": note
        }
    )



@login_required
def delete_note(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    if note.file:

        note.file.delete(
            save=False
        )


    note.delete()


    messages.success(
        request,
        "Lecture note deleted successfully."
    )


    return redirect(
        "notes"
    )

@login_required
def flashcard_setup(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    if request.method == "POST":


        amount = int(
            request.POST.get(
                "amount",
                10
            )
        )


        request.session[
            "flashcard_amount"
        ] = amount



        return redirect(
            "generate_flashcards",
            note_id=note.id
        )



    return render(
        request,
        "notes/flashcard_setup.html",
        {
            "note": note
        }
    )



@login_required
def generate_flashcards(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )


    try:


        amount = request.session.get(
            "flashcard_amount",
            10
        )



        path = note.file.path



        if note.file_type == "pdf":

            text = read_pdf(path)


        elif note.file_type == "docx":

            text = read_docx(path)


        else:

            text = read_txt(path)



        if not text.strip():

            messages.error(
                request,
                "No readable text found."
            )

            return redirect(
                "notes"
            )



        text = text[:5000]



        prompt = f"""

You are a university study assistant.

Create {amount} useful flashcards from the lecture note below.

Return ONLY valid JSON.

Format:

[
{{
"question":"Question",
"answer":"Answer"
}}
]


Rules:

- Do not add markdown.
- Do not add explanations.
- Keep every flashcard unique.
- Use only information from the note.


Lecture Note:

{text}

"""



        response = ask_gemini(
            prompt
        )



        response = response.replace(
            "```json",
            ""
        )

        response = response.replace(
            "```",
            ""
        ).strip()



        match = re.search(
            r"\[.*\]",
            response,
            re.DOTALL
        )



        if not match:

            raise Exception(
                "Invalid flashcard response"
            )



        cards = json.loads(
            match.group(0)
        )



        Flashcard.objects.filter(
            note=note
        ).delete()



        for card in cards:


            Flashcard.objects.create(
                note=note,
                question=card.get(
                    "question",
                    ""
                ),
                answer=card.get(
                    "answer",
                    ""
                )
            )



        if "flashcard_amount" in request.session:

            del request.session[
                "flashcard_amount"
            ]



        messages.success(
            request,
            f"{len(cards)} flashcards generated successfully."
        )



        return redirect(
            "view_flashcards",
            note_id=note.id
        )



    except Exception as e:


        messages.error(
            request,
            f"Flashcard Error: {str(e)}"
        )


        return redirect(
            "notes"
        )



@login_required
def view_flashcards(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user
    )



    flashcards = note.ai_flashcards.all()



    return render(
        request,
        "notes/flashcards.html",
        {
            "note": note,
            "flashcards": flashcards
        }
    )