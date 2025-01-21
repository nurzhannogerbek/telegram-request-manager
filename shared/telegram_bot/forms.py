class ApplicationForm:
    """
    Represents a user-specific application form.
    """

    def __init__(self, lang, localization):
        """
        Initializes the form with the user's language.

        :param lang: The language code (e.g., 'ru', 'kz', 'en').
        :param localization: Localization instance to fetch questions.
        """
        self.lang = lang
        self.questions = localization.get_questions(lang)
        self.responses = {}
        self.current_question = 0

    def get_next_question(self):
        """
        Returns the next question in the form.

        :return: The next question as a string, or None if the form is complete.
        """
        if self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return None

    def save_response(self, response):
        """
        Saves the user's response to the current question.
        """
        self.responses[self.questions[self.current_question]] = response
        self.current_question += 1

    def is_complete(self):
        """
        Checks if the form is complete.

        :return: True if all questions have been answered, False otherwise.
        """
        return self.current_question >= len(self.questions)
