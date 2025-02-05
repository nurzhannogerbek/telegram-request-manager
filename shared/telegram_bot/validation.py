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
        :return: True if valid, False otherwise.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone):
        """
        Validates a phone number using a regular expression.

        :param phone: The phone number as a string.
        :return: True if valid, False otherwise.
        """
        pattern = r"^\+?\d{10,15}$"
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_age(age):
        """
        Validates that the given input is a number representing a valid age.

        :param age: The user's input as a string.
        :return: True if the input is a valid age, False otherwise.
        """
        if age.isdigit():  # Check if input contains only digits.
            age = int(age)  # Convert to an integer.
            return 1 <= age <= 120  # Return True if age is within the acceptable range.
        return False  # Return False if input is not numeric.
