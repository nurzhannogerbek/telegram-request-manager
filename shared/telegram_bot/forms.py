class ApplicationForm:
    """
    Represents a user-specific application form for collecting required data.
    """

    def __init__(self, lang, localization):
        """
        Initializes the form with the user's language and localization settings.

        :param lang: The language code (e.g., 'ru', 'kz', 'en').
        :param localization: Localization instance to fetch questions for the form.
        """
        self.lang = lang  # Stores the user's preferred language.
        self.questions = localization.get_questions(lang)  # Retrieves localized questions for the selected language.
        self.responses = {}  # Dictionary to store user responses.
        self.current_question_index = 0  # Tracks the index of the current question.

    def get_next_question(self):
        """
        Returns the next question as a string, or None if the form is complete.

        :return: The next question as a string.
        """
        if self.current_question_index < len(self.questions):
            # Return only the question text, not the type.
            return self.questions[self.current_question_index]["question"]
        return None  # Return None if the form is complete.

    def get_current_question_type(self):
        """
        Returns the type of the current question.

        :return: The type of the current question as a string, or None if form is complete.
        """
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]["type"]
        return None

    def save_response(self, response):
        """
        Saves the user's response to the current question and moves to the next question.

        :param response: The user's answer to the current question as a string.
        """
        if self.current_question_index < len(self.questions):
            # Use only the question text as the key for responses.
            current_question_text = self.questions[self.current_question_index]["question"]

            response = response.strip()

            # Do not save empty responses; log an error or handle it accordingly.
            if not response:
                raise ValueError("The response cannot be empty.")

            # Save the response with the question text as the key.
            self.responses[current_question_text] = response
            self.current_question_index += 1  # Move to the next question.

    def is_complete(self):
        """
        Checks if the form is complete by ensuring all required questions are answered.

        :return: True if all questions have been answered, False otherwise.
        """
        return self.current_question_index >= len(self.questions)

    def get_unanswered_questions(self):
        """
        Returns a list of unanswered questions for the form.

        :return: A list of unanswered questions as strings.
        """
        unanswered = [
            question for question in self.questions
            if question not in self.responses or not self.responses[question].strip()
        ]
        return unanswered

    def get_all_responses(self):
        """
        Returns a dictionary of all collected responses, mapped by the question titles in the correct order.

        :return: A dictionary where keys match the column headers in the Google Sheet.
        """
        response_mapping = {
            "Ваше полное имя?": "Full Name",
            "Сіздің толық атыңыз?": "Full Name",
            "What is your full name?": "Full Name",
            "Ваш возраст?": "Age",
            "Сіздің жасыңыз?": "Age",
            "How old are you?": "Age",
            "Ваш email?": "Email",
            "Сіздің email?": "Email",
            "What is your email?": "Email",
            "Ваш номер телефона?": "Phone",
            "Сіздің телефон нөміріңіз?": "Phone",
            "What is your phone number?": "Phone",
            "Цель вступления в группу?": "Purpose",
            "Топқа кіру мақсатыңыз қандай?": "Purpose",
            "What is your purpose for joining the group?": "Purpose"
        }
        mapped_responses = {}
        for question, answer in self.responses.items():
            mapped_key = response_mapping.get(question)
            if mapped_key:
                mapped_responses[mapped_key] = answer
        return mapped_responses

