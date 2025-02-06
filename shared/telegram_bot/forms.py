from shared.telegram_bot.logger import logger

class ApplicationForm:
    _cached_questions = {}

    def __init__(self, lang, localization):
        logger.info(f"Creating ApplicationForm for lang={lang}")
        self.lang = lang
        self.responses = []
        self.current_question_index = 0
        if lang not in ApplicationForm._cached_questions:
            logger.info(f"Questions not cached for lang={lang}, fetching from localization.")
            ApplicationForm._cached_questions[lang] = localization.get_questions(lang)
        self.questions = ApplicationForm._cached_questions[lang]
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
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]["question"]
        return None

    def get_current_question_type(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]["type"]
        return None

    def save_response(self, response):
        if self.current_question_index < len(self.questions):
            response = response.strip()
            if not response:
                raise ValueError("The response cannot be empty.")
            current_question_text = self.questions[self.current_question_index]["question"]
            self.responses.append((current_question_text, response))
            self.current_question_index += 1

    def is_complete(self):
        return self.current_question_index >= len(self.questions)

    def get_all_responses(self):
        return {
            self.response_mapping[question]: answer
            for question, answer in self.responses
            if question in self.response_mapping
        }
