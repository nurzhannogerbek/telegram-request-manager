import re


class Validation:
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")
    MAX_EMAIL_LENGTH = 320
    MAX_PHONE_LENGTH = 15
    MAX_AGE = 120

    @staticmethod
    def validate_email(email):
        if not email or len(email) > Validation.MAX_EMAIL_LENGTH:
            return False
        return bool(Validation.EMAIL_PATTERN.fullmatch(email))

    @staticmethod
    def validate_phone(phone):
        if not phone or len(phone) > Validation.MAX_PHONE_LENGTH:
            return False
        return bool(Validation.PHONE_PATTERN.fullmatch(phone))

    @staticmethod
    def validate_age(age):
        if not age.isdigit():
            return False
        age = int(age)
        return 1 <= age <= Validation.MAX_AGE
