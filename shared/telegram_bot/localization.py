class Localization:
    """
    Class to manage language-specific questions for the bot.
    """

    def __init__(self):
        """
        Initializes the localization class with predefined questions.
        """
        self.questions = {
            "ru": ["Ваше полное имя?", "Ваш возраст?", "Ваш email?"],
            "kz": ["Сіздің толық атыңыз?", "Сіздің жасыңыз?", "Сіздің email?"],
            "en": ["What is your full name?", "How old are you?", "What is your email?"]
        }

    def get_questions(self, lang):
        """
        Retrieves the list of questions for a specified language.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :return: List of questions in the specified language. Defaults to English if the language is not found.
        """
        return self.questions.get(lang, self.questions["en"])
