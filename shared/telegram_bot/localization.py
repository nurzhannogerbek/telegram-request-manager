class Localization:
    """
    Class to manage language-specific strings and questions for the bot.
    """

    def __init__(self):
        """
        Initializes the localization class with predefined strings and questions.
        """
        self.strings = {
            "ru": {
                "privacy_accept": "Согласен",
                "privacy_decline": "Не согласен",
                "privacy_prompt": "Для продолжения прочтите и примите политику конфиденциальности.",
                "start_questionnaire": "Спасибо! Пожалуйста, ответьте на вопрос:",
                "decline_message": "Вы отказались от условий. Диалог завершён.",
                "choose_language": "Пожалуйста, выберите язык:",
                "application_complete": "Спасибо! Ваша заявка принята.",
                "fill_missing_data": "Вы не предоставили все необходимые данные. Ваша заявка отклонена.",
                "error_message": "Произошла ошибка. Пожалуйста, попробуйте позже.",
            },
            "kz": {
                "privacy_accept": "Қабылдаймын",
                "privacy_decline": "Қабылдамаймын",
                "privacy_prompt": "Жалғастыру үшін құпиялылық саясатын оқып, келісіңіз.",
                "start_questionnaire": "Рахмет! Сұраққа жауап беріңіз:",
                "decline_message": "Сіз шарттарды қабылдамадыңыз. Диалог аяқталды.",
                "choose_language": "Тілді таңдаңыз:",
                "application_complete": "Рақмет! Сіздің өтініміңіз қабылданды.",
                "fill_missing_data": "Сіз барлық қажетті деректерді бермедіңіз. Сіздің өтініміңіз қабылданбады.",
                "error_message": "Қате орын алды. Кейінірек қайталап көріңіз.",
            },
            "en": {
                "privacy_accept": "Agree",
                "privacy_decline": "Disagree",
                "privacy_prompt": "To continue, please read and accept the privacy policy.",
                "start_questionnaire": "Thank you! Please answer the question:",
                "decline_message": "You have declined the terms. The dialog is closed.",
                "choose_language": "Please choose your language:",
                "application_complete": "Thank you! Your application has been accepted.",
                "fill_missing_data": "You did not provide all the required data. Your application has been declined.",
                "error_message": "An error occurred. Please try again later.",
            },
        }

        self.questions = {
            "ru": [
                "Ваше полное имя?",
                "Ваш возраст?",
                "Ваш email?",
                "Ваш номер телефона?",
                "Цель вступления в группу?",
            ],
            "kz": [
                "Сіздің толық атыңыз?",
                "Сіздің жасыңыз?",
                "Сіздің email?",
                "Сіздің телефон нөміріңіз?",
                "Топқа кіру мақсатыңыз қандай?",
            ],
            "en": [
                "What is your full name?",
                "How old are you?",
                "What is your email?",
                "What is your phone number?",
                "What is your purpose for joining the group?",
            ],
        }

    def get_string(self, lang, key):
        """
        Retrieves a localized string by key.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :param key: Key for the localized string.
        :return: Localized string or the key itself if not found.
        """
        return self.strings.get(lang, self.strings["en"]).get(key, key)

    def get_questions(self, lang):
        """
        Retrieves the list of questions for a specified language.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :return: List of questions in the specified language. Defaults to English if the language is not found.
        """
        return self.questions.get(lang, self.questions["en"])
