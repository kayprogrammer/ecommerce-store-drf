from django.core.validators import RegexValidator

PHONE_REGEX_VALIDATOR = RegexValidator(
    regex=r"^\+\d{10,15}$",
    message="Enter a valid phone number. Format: '+1234567890'. Up to 15 digits allowed.",
)
