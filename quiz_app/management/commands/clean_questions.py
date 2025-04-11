from django.core.management.base import BaseCommand
from quiz_app.models import Question
import html

class Command(BaseCommand):
    help = 'Cleans question and answer text in the database'

    def handle(self, *args, **options):
        for question in Question.objects.all():
            original_question = question.question_text
            original_answer = question.correct_answer

            # Clean the question and the correct answer
            question.question_text = html.unescape(original_question)
            question.correct_answer = html.unescape(original_answer)

            # Clean wrong answers
            for i, answer in enumerate(question.wrong_answers):
                question.wrong_answers[i] = html.unescape(answer)

            # Save the cleaned question
            question.save()

        self.stdout.write(self.style.SUCCESS('✅ All questions cleaned!'))
