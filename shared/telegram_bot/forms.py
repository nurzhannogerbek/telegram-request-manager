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
        self.questions = localization.get_questions(lang)  # Retrieves localized questions.
        self.responses = {}  # Dictionary to store user responses.
        self.current_question = 0  # Tracks the index of the current question.

    def get_next_question(self):
        """
        Returns the next question in the form.

        :return: The next question as a string, or None if the form is complete.
        """
        if self.current_question < len(self.questions):
            # Returns the next question based on the current index.
            return self.questions[self.current_question]
        return None  # Indicates that all questions have been answered.

    def save_response(self, response):
        """
        Saves the user's response to the current question.

        :param response: The user's answer to the current question as a string.
        """
        # Maps the current question to the user's response.
        self.responses[self.questions[self.current_question]] = response
        self.current_question += 1  # Moves to the next question.

    def is_complete(self):
        """
        Checks if the form is complete by ensuring all required questions are answered.

        :return: True if all questions have been answered, False otherwise.
        """
        # Iterates through all questions to verify if each has a corresponding response.
        for question in self.questions:
            if question not in self.responses or not self.responses[question].strip():
                return False  # Returns False if any question is unanswered or blank.
        return True  # Returns True if all questions are answered.

    def get_unanswered_questions(self):
        """
        Returns a list of unanswered questions for the form.

        :return: A list of unanswered questions as strings.
        """
        unanswered = []
        for question in self.questions:
            if question not in self.responses or not self.responses[question].strip():
                unanswered.append(question)
        return unanswered
