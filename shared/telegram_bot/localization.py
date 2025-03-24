class Localization:
    """
    Manages localized strings and questions for the Telegram bot in multiple languages.
    Provides utility methods to retrieve strings and questions based on the selected language.
    """
    # Dictionary containing localized strings in different languages.
    STRINGS = {
        "ru": {
            "privacy_accept": "Согласен",
            "privacy_decline": "Не согласен",
            "privacy_prompt": "Чтобы продолжить, пожалуйста, ознакомьтесь с политикой конфиденциальности. В ней описано, как мы обрабатываем и защищаем ваши данные.",
            "start_questionnaire": "Чтобы мы могли лучше вас узнать, пожалуйста, ответьте на несколько вопросов.",
            "decline_message": "Вы решили не принимать условия в данный момент. Если передумаете, мы будем здесь!",
            "choose_language": "Чтобы продолжить, выберите предпочитаемый язык:",
            "application_complete": "Спасибо, что ответили на наши вопросы! Ваша заявка принята, рады приветствовать вас в сообществе.",
            "fill_missing_data": "Кажется, вы не предоставили всю необходимую информацию. Ваша заявка отклонена, но вы можете снова подать заявку на вступление в группу, когда будете готовы.",
            "error_message": "Ой, что-то пошло не так. Пожалуйста, попробуйте позже или обратитесь в поддержку.",
            "privacy_policy_request": "Пожалуйста, выделите минутку, чтобы ознакомиться с нашей политикой конфиденциальности, где описано, как мы обрабатываем ваши данные.",
            "form_reminder": "Мы заметили, что вы ещё не закончили заполнение анкеты. Пожалуйста, ответьте на все вопросы, чтобы получить доступ в группу.",
            "show_more": "Показать полностью",
            "privacy_policy_link_text": "Нажмите здесь, чтобы ознакомиться с политикой конфиденциальности.",
            "invalid_email": "Похоже, это неправильный формат адреса электронной почты. Пожалуйста, введите адрес вида 'name@example.com'.",
            "invalid_phone": "Пожалуйста, введите действительный номер телефона в формате +XXXXXXXX..., включая код страны.",
            "invalid_age": "Укажите корректный возраст от 1 до 120 лет.",
            "press_button": "Пожалуйста, нажмите кнопку на экране."
        },
        "kz": {
            "privacy_accept": "Қабылдаймын",
            "privacy_decline": "Қабылдамаймын",
            "privacy_prompt": "Жалғастыру үшін біздің құпиялылық саясатымен танысып шығыңыз. Онда деректеріңіздің қалай сақталатыны және қорғалатыны туралы жазылған.",
            "start_questionnaire": "Біз сізді жақынырақ танып білу үшін бірнеше сұраққа жауап беріңіз.",
            "decline_message": "Сіз осы сәтте шарттарды қабылдамадыңыз. Ойыңызды өзгертсеңіз, біз әрдайым осындамыз!",
            "choose_language": "Жалғастыру үшін өзіңізге ыңғайлы тілді таңдаңыз:",
            "application_complete": "Сұрақтарға уақыт бөліп жауап бергеніңізге рақмет! Сіздің өтініміңіз қабылданды, қауымдастыққа қош келдіңіз.",
            "fill_missing_data": "Сіз барлық қажетті ақпаратты бермеген сияқтысыз. Өтініміңіз қабылданбады, бірақ дайын болған кезіңізде қайта өтінім бере аласыз.",
            "error_message": "Упс, бірдеңе қате кетті. Кейінірек қайталап көріңіз немесе қолдау қызметіне хабарласыңыз.",
            "privacy_policy_request": "Жеке мәліметтеріңізді қалай өңдейтініміз жайлы толығырақ білу үшін құпиялылық саясатымен танысып шығыңыз.",
            "form_reminder": "Әлі анкетаны толық аяқтамаған сияқтысыз. Топқа кіру үшін барлық сұрақтарға жауап беріңіз.",
            "show_more": "Толығырақ көрсету",
            "privacy_policy_link_text": "Құпиялылық саясатына сілтемені көру үшін мұнда басыңыз.",
            "invalid_email": "Бұл электрондық пошта мекенжайы дұрыс форматқа сай емес. Мысалы: 'name@example.com'.",
            "invalid_phone": "Телефон нөміріңізді + белгісімен және цифрлармен (ел коды) енгізіңіз. Мысалы, +77001234567.",
            "invalid_age": "Жасыңызды 1 мен 120 аралығында дұрыс енгізіңіз.",
            "press_button": "Түймені басыңыз."
        },
        "en": {
            "privacy_accept": "Agree",
            "privacy_decline": "Disagree",
            "privacy_prompt": "To continue, please read and accept our privacy policy. It explains how we handle and protect your data.",
            "start_questionnaire": "Please help us get to know you better by answering a few short questions.",
            "decline_message": "You've chosen not to accept the terms at this time. We're here if you change your mind!",
            "choose_language": "To continue, please choose your preferred language:",
            "application_complete": "Thank you for taking the time to answer our questions! Your application has been accepted — welcome to the community.",
            "fill_missing_data": "It looks like you didn't provide all the required information. Your application has been declined, but you can apply again when you're ready.",
            "error_message": "Oops, something went wrong. Please try again later or contact support.",
            "privacy_policy_request": "Please take a moment to review our privacy policy, which explains how we handle your data.",
            "form_reminder": "We noticed you haven't finished filling out the form. Please answer all the questions to gain access to the group.",
            "show_more": "Show more",
            "privacy_policy_link_text": "Click here to view the Privacy Policy.",
            "invalid_email": "That doesn't look like a valid email address. Please use a format like 'name@example.com'.",
            "invalid_phone": "Please enter a valid phone number in the format +XXXXXXXX..., including your country code if necessary.",
            "invalid_age": "Please enter a valid age between 1 and 120.",
            "press_button": "Please press the button on the screen."
        }
    }

    QUESTIONS = {
        "ru": [
            {"question": "Как мы можем к вам обращаться? Введите, пожалуйста, ваше полное имя.", "type": "text"},
            {"question": "Сколько вам лет?", "type": "age"},
            {"question": "Укажите ваш адрес электронной почты (например: name@example.com).", "type": "email"},
            {"question": "Какой у вас номер телефона? Пожалуйста, укажите его в формате +XXXXXXXX....", "type": "phone"},
            {"question": "Расскажите, зачем вы хотите присоединиться к нашей группе?", "type": "text"},
            {"question": "Какой у вас род деятельности?", "type": "text"},
            {"question": "Какое у вас место работы?", "type": "text"},
            {"question": "В каком городе вы проживаете?", "type": "text"},
            {"question": "Какой у вас инстаграм?", "type": "text"},
            {"question": "Откуда вы узнали про нас?", "type": "text"}
        ],
        "kz": [
            {"question": "Сізге қалай жүгінуге болады? Толық атыңызды енгізіңіз, өтінеміз.", "type": "text"},
            {"question": "Жасыңыз қаншада?", "type": "age"},
            {"question": "Электрондық пошта мекенжайыңызды көрсетіңіз (мысалы: name@example.com).", "type": "email"},
            {"question": "Телефон нөміріңіз қандай? Оны +XXXXXXXX... форматында енгізіңіз, өтінеміз.", "type": "phone"},
            {"question": "Біздің топқа не үшін қосылғыңыз келеді?", "type": "text"},
            {"question": "Сіздің қызметіңіз қандай?", "type": "text"},
            {"question": "Сіз қай жерде жұмыс істейсіз?", "type": "text"},
            {"question": "Сіз қай қалада тұрасыз?", "type": "text"},
            {"question": "Сіздің инстаграмыңыз қандай?", "type": "text"},
            {"question": "Біз туралы қайдан білдіңіз?", "type": "text"}
        ],
        "en": [
            {"question": "How should we address you? Please enter your full name.", "type": "text"},
            {"question": "How old are you?", "type": "age"},
            {"question": "Please provide your email address (e.g., name@example.com).", "type": "email"},
            {"question": "What is your phone number? Please enter it in the format +XXXXXXXX....", "type": "phone"},
            {"question": "Please tell us why you want to join our group.", "type": "text"},
            {"question": "What is your occupation?", "type": "text"},
            {"question": "Where do you work?", "type": "text"},
            {"question": "In which city do you live?", "type": "text"},
            {"question": "What's your Instagram?", "type": "text"},
            {"question": "How did you hear about us?", "type": "text"}
        ]
    }

    WELCOME_MESSAGE_MULTILANG = (
        "Welcome! Қош келдіңіз! Добро пожаловать!\n\n"
        "You have applied to join the Qazaq IT Community. Thank you for your interest! "
        "To proceed with membership, please fill out a short questionnaire.\n\n"
        "Сіз Qazaq IT Community тобына қосылуға өтінім қалдырдыңыз. Біз сізге ризамыз! "
        "Топқа кіруді жалғастыру үшін қысқа анкетаны толтырыңыз.\n\n"
        "Вы подали заявку на вступление в группу Qazaq IT Community. Благодарим вас за интерес! "
        "Чтобы продолжить вступление, пожалуйста, заполните короткую анкету.\n\n"
        "To continue, please choose a language:\n"
        "Жалғастыру үшін тілді таңдаңыз:\n"
        "Для продолжения выберите язык:"
    )

    PRESS_BUTTON_MULTILANG = (
        "Пожалуйста, нажмите одну из кнопок.\n"
        "Түймені басыңыз.\n"
        "Please press one of the buttons."
    )

    @staticmethod
    def get_string(lang, key):
        """
        Retrieves a localized string based on the language and key.

        Args:
            lang (str): The language code (e.g., 'en', 'ru', 'kz').
            key (str): The key representing the string to retrieve.

        Returns:
            str: The localized string if found, otherwise the key itself.
        """
        return Localization.STRINGS.get(lang, Localization.STRINGS["en"]).get(key, key)

    @staticmethod
    def get_multilang_welcome_message():
        """
        Retrieves the multilingual welcome message.

        Returns:
            str: The welcome message containing greetings in multiple languages.
        """
        return Localization.WELCOME_MESSAGE_MULTILANG

    @staticmethod
    def get_questions(lang):
        """
        Retrieves the list of questions for the specified language.

        Args:
            lang (str): The language code (e.g., 'en', 'ru', 'kz').

        Returns:
            list: A list of dictionaries, each containing a question and its type.
        """
        return Localization.QUESTIONS.get(lang, Localization.QUESTIONS["en"])
