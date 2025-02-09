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
            "Как мы можем к вам обращаться? Введите, пожалуйста, ваше полное имя.": "Full Name",
            "Сколько вам лет?": "Age",
            "Укажите ваш адрес электронной почты (например: name@example.com).": "Email",
            "Какой у вас номер телефона? Пожалуйста, укажите его в формате +XXXXXXXX....": "Phone",
            "Расскажите, зачем вы хотите присоединиться к нашей группе?": "Purpose",
            "Какой у вас род деятельности?": "Occupation",
            "Какое у вас место работы?": "Workplace",
            "В каком городе вы проживаете?": "City",
            "Сізге қалай жүгінуге болады? Толық атыңызды енгізіңіз, өтінеміз.": "Full Name",
            "Жасыңыз қаншада?": "Age",
            "Электрондық пошта мекенжайыңызды көрсетіңіз (мысалы: name@example.com).": "Email",
            "Телефон нөміріңіз қандай? Оны +XXXXXXXX... форматында енгізіңіз, өтінеміз.": "Phone",
            "Біздің топқа не үшін қосылғыңыз келеді?": "Purpose",
            "Сіздің қызметіңіз қандай?": "Occupation",
            "Сіз қай жерде жұмыс істейсіз?": "Workplace",
            "Сіз қай қалада тұрасыз?": "City",
            "How should we address you? Please enter your full name.": "Full Name",
            "How old are you?": "Age",
            "Please provide your email address (e.g., name@example.com).": "Email",
            "What is your phone number? Please enter it in the format +XXXXXXXX....": "Phone",
            "Please tell us why you want to join our group.": "Purpose",
            "What is your occupation?": "Occupation",
            "Where do you work?": "Workplace",
            "In which city do you live?": "City"
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
