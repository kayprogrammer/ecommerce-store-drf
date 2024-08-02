from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from apps.common.managers import GetOrNoneManager


class CustomUserManager(BaseUserManager, GetOrNoneManager):
    """
    Custom manager for the User model.

    Methods:
        email_validator(email):
            Validates the given email address.

        create_user(first_name, last_name, email, password, **extra_fields):
            Creates and saves a regular user with the given details.

        create_superuser(first_name, last_name, email, password, **extra_fields):
            Creates and saves a superuser with the given details.
    """

    def email_validator(self, email):
        """
        Validates the given email address.

        Args:
            email (str): The email address to validate.

        Raises:
            ValueError: If the email address is not valid.
        """
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email address"))

    def validate_user(self, first_name, last_name, email):
        if not first_name:
            raise ValueError(_("Users must submit a first name"))

        if not last_name:
            raise ValueError(_("Users must submit a last name"))

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Base User Account: An email address is required"))

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        """
        Creates and saves a regular user with the given details.

        Args:
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            email (str): The email address of the user.
            password (str): The password for the user.
            **extra_fields: Additional fields for the user.

        Raises:
            ValueError: If any required field is missing or invalid.

        Returns:
            User: The created user instance.
        """
        self.validate_user(first_name, last_name, email)

        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user.save(using=self._db)
        return user

    async def acreate_user(
        self, first_name, last_name, email, password, **extra_fields
    ):
        self.validate_user(first_name, last_name, email)
        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        await user.asave(using=self._db)
        return user

    def validate_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superusers must have is_staff=True"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superusers must have is_superuser=True"))

        if not password:
            raise ValueError(_("Superusers must have a password"))

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Admin Account: An email address is required"))
        return extra_fields

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given details.

        Args:
            first_name (str): The first name of the superuser.
            last_name (str): The last name of the superuser.
            email (str): The email address of the superuser.
            password (str): The password for the superuser.
            **extra_fields: Additional fields for the superuser.

        Raises:
            ValueError: If any required field is missing or invalid.

        Returns:
            User: The created superuser instance.
        """
        extra_fields = self.validate_superuser(email, password, **extra_fields)
        user = self.create_user(first_name, last_name, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def acreate_superuser(
        self, first_name, last_name, email, password, **extra_fields
    ):
        extra_fields = self.validate_superuser(email, password, **extra_fields)
        user = await self.acreate_user(
            first_name, last_name, email, password, **extra_fields
        )
        return user
