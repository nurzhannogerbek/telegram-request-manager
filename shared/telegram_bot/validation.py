import re

class Validation:
    """
    Provides validation methods for user inputs such as email addresses, phone numbers, and age.
    Ensures that the data provided by users meets expected formats and constraints.
    """

    # Regular expression pattern to validate email addresses.
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    # Regular expression pattern to validate phone numbers (allows optional '+' and digits).
    PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")
    # Maximum allowable length for email addresses.
    MAX_EMAIL_LENGTH = 320
    # Maximum allowable length for phone numbers.
    MAX_PHONE_LENGTH = 15
    # Maximum allowable age.
    MAX_AGE = 120

    @staticmethod
    def validate_email(email):
        """
        Validates the given email address to ensure it follows a proper format and length constraint.

        Args:
            email (str): The email address provided by the user.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        # Check if the email is present and does not exceed the maximum length.
        if not email or len(email) > Validation.MAX_EMAIL_LENGTH:
            return False
        # Use the regular expression to validate the email format.
        return bool(Validation.EMAIL_PATTERN.fullmatch(email))

    @staticmethod
    def validate_phone(phone):
        """
        Validates the given phone number to ensure it follows the correct format and length.

        Args:
            phone (str): The phone number provided by the user.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        # Check if the phone number is present and does not exceed the maximum length.
        if not phone or len(phone) > Validation.MAX_PHONE_LENGTH:
            return False
        # Use the regular expression to validate the phone number format.
        return bool(Validation.PHONE_PATTERN.fullmatch(phone))

    @staticmethod
    def validate_age(age):
        """
        Validates the given age to ensure it is a numeric value within a permissible range.

        Args:
            age (str): The age provided by the user as a string.

        Returns:
            bool: True if the age is a valid numeric value within the range, False otherwise.
        """
        # Check if the age is a valid digit.
        if not age.isdigit():
            return False
        # Convert the age to an integer and ensure it is within the allowed range.
        age = int(age)
        return 1 <= age <= Validation.MAX_AGE
