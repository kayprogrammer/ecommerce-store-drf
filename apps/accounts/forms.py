from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from django.contrib.auth import get_user_model

User = get_user_model()

# -----ADMIN USER CREATION AND AUTHENTICATION------------#


class CustomAdminUserCreationForm(UserCreationForm):
    """
    A form for creating new admin users, with all required fields and
    repeated password.

    Attributes:
        Meta (class): Inner class to provide metadata to the form.
            model (User): The model associated with this form.
            fields (list): The fields to be used in the form.
            error_class (str): CSS class for error messages.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email", "first_name", "last_name"]
        error_class = "error"


class CustomAdminUserChangeForm(UserChangeForm):
    """
    A form for updating existing admin users, with all required fields.

    Attributes:
        Meta (class): Inner class to provide metadata to the form.
            model (User): The model associated with this form.
            fields (list): The fields to be used in the form.
            error_class (str): CSS class for error messages.
    """

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        error_class = "error"
