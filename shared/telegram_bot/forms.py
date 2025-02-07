class ApplicationForm:
    """
    Manages the questionnaire flow for users interacting with the Telegram bot.
    Stores and tracks user responses while ensuring that questions are asked sequentially.
    Implements validation mechanisms and mapping between questions and internal response fields.

    Attributes:
        lang (str): The language selected by the user.
        responses (list): A list of tuples containing question-response pairs.
        current_question_index (int): Tracks the index of the current question being asked.
        questions (list): The set of questions to be asked, loaded based on the selected language.
        response_mapping (dict): Maps questions to internal response field names.
    """
    _cached_questions = {}  # Cache to store localized questions for performance optimization.

    def __init__(self, lang, localization):
        """
        Initializes the application form for the given language and loads the questions.

        Args:
            lang (str): The language code (e.g., 'en', 'ru', 'kz').
            localization (Localization): The localization object for retrieving questions.
        """
        self.lang = lang
        self.responses = []
        self.current_question_index = 0

        # Check if the questions for the specified language are already cached.
        if lang not in ApplicationForm._cached_questions:
            # If not cached, fetch and cache the questions.
            ApplicationForm._cached_questions[lang] = localization.get_questions(lang)

        # Load the questions from the cache.
        self.questions = ApplicationForm._cached_questions[lang]

        # Map the questions to internal response fields.
        self.response_mapping = {
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

    def get_next_question(self):
        """
        Retrieves the next question in the sequence based on the current question index.

        Returns:
            str or None: The next question to be asked, or None if all questions have been answered.
        """
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]["question"]
        return None

    def get_current_question_type(self):
        """
        Retrieves the type of the current question (e.g., 'text', 'email', 'phone', 'age').

        Returns:
            str or None: The type of the current question, or None if no questions remain.
        """
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]["type"]
        return None

    def save_response(self, response):
        """
        Saves the user's response to the current question and advances to the next question.

        Args:
            response (str): The user's response to the current question.

        Raises:
            ValueError: If the response is empty.
        """
        response = response.strip()
        if not response:
            raise ValueError("The response cannot be empty.")

        # Get the text of the current question.
        current_question_text = self.questions[self.current_question_index]["question"]

        # Ensure the responses list is valid.
        if not isinstance(self.responses, list):
            self.responses = []

        # Append the question-response pair to the responses list.
        self.responses.append((current_question_text, response))

        # Move to the next question.
        self.current_question_index += 1

    def is_complete(self):
        """
        Checks whether all questions have been answered.

        Returns:
            bool: True if the form is complete, False otherwise.
        """
        return self.current_question_index >= len(self.questions)

    def get_all_responses(self):
        """
        Compiles all collected responses and maps them to the corresponding internal response fields.

        Returns:
            dict: A dictionary where keys are internal response field names and values are the user's responses.
        """
        return {
            self.response_mapping[question]: answer
            for question, answer in self.responses
            if question in self.response_mapping
        }
