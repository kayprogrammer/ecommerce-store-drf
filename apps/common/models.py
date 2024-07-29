import secrets
from typing import Any
import uuid
from django.db import models
from .managers import GetOrNoneManager


class BaseModel(models.Model):
    """
    A base model class that includes common fields and methods for all models.

    Attributes:
        id (UUIDField): Unique identifier for the model instance.
        created_at (DateTimeField): Timestamp when the instance was created.
        updated_at (DateTimeField): Timestamp when the instance was last updated.
    """

    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = GetOrNoneManager()

    class Meta:
        abstract = True

    @property
    def image_url(self):
        """
        Retrieve the URL of the image associated with the model instance.

        Returns:
            str: URL of the image or None if the image is not available.
        """
        url = None
        if hasattr(self, "image"):
            try:
                url = self.image.url
            except:
                url = None
        return url

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


def generate_unique_code(model: BaseModel, field: str) -> str:
    """
    Generate a unique code for a specified model and field.

    Args:
        model (BaseModel): The model class to check for uniqueness.
        field (str): The field name to check for uniqueness.

    Returns:
        str: A unique code.
    """
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    unique_code = "".join(secrets.choice(allowed_chars) for _ in range(12))
    code = unique_code
    similar_object_exists = model.objects.filter(**{field: code}).exists()
    if not similar_object_exists:
        return code
    return generate_unique_code(model, field)


def image_folder_to_upload(subfolder: str = "") -> str:
    """
    Generate a folder path for uploading images.

    Args:
        subfolder (str): The subfolder within the main folder. Defaults to an empty string.

    Returns:
        str: The folder path for uploading images.
    """
    folder = f"ecommerce-store/{subfolder}/"
    if subfolder == "":
        folder = "ecommerce-store/"
    return folder
