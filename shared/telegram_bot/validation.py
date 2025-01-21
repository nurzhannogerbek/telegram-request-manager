import re

class Validation:
    """
    Class to handle input validation for user data.
    """

    @staticmethod
    def validate_email(email):
        """
        Validates an email address using a regular expression.

        :param email: The email address as a string.
        :return: Match object if valid, None otherwise.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        return re.match(pattern, email)

    @staticmethod
    def validate_phone(phone):
        """
        Validates a phone number using a regular expression.

        :param phone: The phone number as a string.
        :return: Match object if valid, None otherwise.
        """
        pattern = r"^\\+?\\d{10,15}$"
        return re.match(pattern, phone)
