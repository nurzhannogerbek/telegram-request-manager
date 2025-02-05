class Localization:
    """
    Class to manage language-specific strings and questions for the bot.
    Provides a centralized way to retrieve text strings and questions based on the user's selected language.
    """

    def __init__(self):
        """
        Initializes the localization class with predefined strings and questions.
        Strings and questions are stored in dictionaries for multiple languages.
        """
        # Dictionary containing text strings for multiple languages.
        self.strings = {
            "ru": {
                "privacy_accept": "Согласен",
                "privacy_decline": "Не согласен",
                "privacy_prompt": "Для продолжения прочтите и примите политику конфиденциальности.",
                "start_questionnaire": "Пожалуйста, ответьте на вопрос:",
                "decline_message": "Вы отказались от условий. Диалог завершён.",
                "choose_language": "Для продолжения выберите язык:",
                "application_complete": "Спасибо! Ваша заявка принята.",
                "fill_missing_data": "Вы не предоставили все необходимые данные. Ваша заявка отклонена.",
                "error_message": "Произошла ошибка. Пожалуйста, попробуйте позже.",
                "privacy_policy_request": "Ознакомьтесь с нашей политикой конфиденциальности.",
                "form_reminder": "Напоминаем, что вы не закончили заполнение анкеты. Пожалуйста, завершите её, чтобы получить доступ к группе.",
                "show_more": "Показать полностью",
                "privacy_policy_link_text": "Нажмите здесь, чтобы ознакомиться с политикой конфиденциальности.",
                "invalid_email": "Пожалуйста, введите корректный адрес электронной почты.",
                "invalid_phone": "Пожалуйста, введите корректный номер телефона.",
                "invalid_age": "Пожалуйста, введите корректный возраст (от 1 до 120)."
            },
            "kz": {
                "privacy_accept": "Қабылдаймын",
                "privacy_decline": "Қабылдамаймын",
                "privacy_prompt": "Жалғастыру үшін құпиялылық саясатын оқып, келісіңіз.",
                "start_questionnaire": "Сұраққа жауап беріңіз:",
                "decline_message": "Сіз шарттарды қабылдамадыңыз. Диалог аяқталды.",
                "choose_language": "Жалғастыру үшін тілді таңдаңыз:",
                "application_complete": "Рақмет! Сіздің өтініміңіз қабылданды.",
                "fill_missing_data": "Сіз барлық қажетті деректерді бермедіңіз. Сіздің өтініміңіз қабылданбады.",
                "error_message": "Қате орын алды. Кейінірек қайталап көріңіз.",
                "privacy_policy_request": "Құпиялылық саясатымен танысыңыз.",
                "form_reminder": "Сіз анкетаны толтырып бітірген жоқсыз. Топқа кіру үшін анкетаны аяқтаңыз.",
                "show_more": "Толығырақ көрсету",
                "privacy_policy_link_text": "Құпиялылық саясатына сілтемені қарау үшін мұнда басыңыз.",
                "invalid_email": "Дұрыс электрондық пошта мекенжайын енгізіңіз.",
                "invalid_phone": "Дұрыс телефон нөмірін енгізіңіз.",
                "invalid_age": "Дұрыс жасты енгізіңіз (1-ден 120-ға дейін)."
            },
            "en": {
                "privacy_accept": "Agree",
                "privacy_decline": "Disagree",
                "privacy_prompt": "To continue, please read and accept the privacy policy.",
                "start_questionnaire": "Please answer the question:",
                "decline_message": "You have declined the terms. The dialog is closed.",
                "choose_language": "To continue, please choose a language:",
                "application_complete": "Thank you! Your application has been accepted.",
                "fill_missing_data": "You did not provide all the required data. Your application has been declined.",
                "error_message": "An error occurred. Please try again later.",
                "privacy_policy_request": "Please review our privacy policy.",
                "form_reminder": "Reminder: You have not completed the form. Please finish it to gain access to the group.",
                "show_more": "Show more",
                "privacy_policy_link_text": "Click here to view the Privacy Policy.",
                "invalid_email": "Please enter a valid email address.",
                "invalid_phone": "Please enter a valid phone number.",
                "invalid_age": "Please enter a valid age (between 1 and 120)."
            }
        }

        # Combined multilingual welcome message.
        self.welcome_message_multilang = (
            "Welcome! Қош келдіңіз! Добро пожаловать!\n\n"
            "To continue, please choose a language:\n"
            "Жалғастыру үшін тілді таңдаңыз:\n"
            "Для продолжения выберите язык:"
        )

        # Dictionary containing questions for multiple languages.
        self.questions = {
            "ru": [
                {"question": "Ваше полное имя?", "type": "text"},
                {"question": "Ваш возраст?", "type": "age"},
                {"question": "Ваш email?", "type": "email"},
                {"question": "Ваш номер телефона?", "type": "phone"},
                {"question": "Цель вступления в группу?", "type": "text"}
            ],
            "kz": [
                {"question": "Сіздің толық атыңыз?", "type": "text"},
                {"question": "Сіздің жасыңыз?", "type": "age"},
                {"question": "Сіздің email?", "type": "email"},
                {"question": "Сіздің телефон нөміріңіз?", "type": "phone"},
                {"question": "Топқа кіру мақсатыңыз қандай?", "type": "text"}
            ],
            "en": [
                {"question": "What is your full name?", "type": "text"},
                {"question": "How old are you?", "type": "age"},
                {"question": "What is your email?", "type": "email"},
                {"question": "What is your phone number?", "type": "phone"},
                {"question": "What is your purpose for joining the group?", "type": "text"}
            ]
        }

    def get_string(self, lang, key):
        """
        Retrieves a localized string by key.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :param key: Key for the localized string.
        :return: Localized string or the key itself if not found.
        """
        return self.strings.get(lang, self.strings["en"]).get(key, key)

    def get_multilang_welcome_message(self):
        """
        Retrieves the combined multilingual welcome message.

        :return: A string containing the welcome message in Russian, Kazakh, and English.
        """
        return self.welcome_message_multilang

    def get_questions(self, lang):
        """
        Retrieves the list of questions for a specified language.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :return: List of questions in the specified language. Defaults to English if the language is not found.
        """
        return self.questions.get(lang, self.questions["en"])
