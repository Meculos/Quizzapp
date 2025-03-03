import requests
from django.core.management.base import BaseCommand
from quiz_app.models import Question

class Command(BaseCommand):
    help = "Fetch and store anime trivia questions from OpenTDB"

    TOKEN_URL = "https://opentdb.com/api_token.php?command=request"
    API_URL = "https://opentdb.com/api.php?amount=50&category=32&type=multiple&token={}"

    def handle(self, *args, **kwargs):
        # Step 1: Request a session token
        token_response = requests.get(self.TOKEN_URL)
        if token_response.status_code != 200:
            self.stderr.write("Error requesting session token from OpenTDB.")
            return

        token_data = token_response.json()
        if token_data["response_code"] != 0:
            self.stderr.write("Failed to retrieve a valid session token.")
            return
        
        session_token = token_data["token"]

        # Step 2: Fetch questions with the token
        response = requests.get(self.API_URL.format(session_token))
        if response.status_code != 200:
            self.stderr.write("Error fetching questions from OpenTDB.")
            return

        data = response.json()
        if data["response_code"] != 0:
            self.stderr.write("API returned an error. Session token might be expired.")
            return

        # Step 3: Store questions in the database
        count = 0
        for item in data["results"]:
            question_text = item["question"]
            correct_answer = item["correct_answer"]
            wrong_answers = item["incorrect_answers"]  # This contains a list of 3 wrong answers

            # Save to database if it doesn’t already exist
            if not Question.objects.filter(question_text=question_text).exists():
                Question.objects.create(
                    question_text=question_text,
                    category="cartoons",
                    correct_answer=correct_answer,
                    wrong_answers=wrong_answers
                )
                count += 1

        self.stdout.write(f"Successfully added {count} new questions to the database.")

