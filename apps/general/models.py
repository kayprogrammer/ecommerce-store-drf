from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class SiteDetail(BaseModel):
    """
    Model to store the details of the site or application.

    Fields:
        name (CharField): The name of the site, default is "E-STORE".
        email (EmailField): Contact email address, default is "kayprogrammer1@gmail.com".
        phone (CharField): Contact phone number, default is "+2348133831036".
        address (CharField): Physical address, default is "234, Lagos, Nigeria".
        fb (CharField): Facebook page URL, default is "https://facebook.com".
        tw (CharField): Twitter page URL, default is "https://twitter.com".
        wh (CharField): Whatsapp contact URL, default is "https://wa.me/2348133831036".
        ig (CharField): Instagram page URL, default is "https://instagram.com".

    Methods:
        __str__(): Returns the name of the site.
        save(*args, **kwargs): Ensures that only one instance of SiteDetail can exist.
    """

    name = models.CharField(max_length=300, default="E-STORE")
    email = models.EmailField(default="kayprogrammer1@gmail.com")
    phone = models.CharField(max_length=300, default="+2348133831036")
    address = models.CharField(max_length=300, default="234, Lagos, Nigeria")
    fb = models.CharField(
        max_length=300, verbose_name=_("Facebook"), default="https://facebook.com"
    )
    tw = models.CharField(
        max_length=300, verbose_name=_("Twitter"), default="https://twitter.com"
    )
    wh = models.CharField(
        max_length=300,
        verbose_name=_("Whatsapp"),
        default="https://wa.me/2348133831036",
    )
    ig = models.CharField(
        max_length=300, verbose_name=_("Instagram"), default="https://instagram.com"
    )

    def __str__(self):
        """
        Returns the name of the site.

        Returns:
            str: The name of the site.
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure that only one instance of SiteDetail can exist.

        Raises:
            ValidationError: If an attempt is made to create more than one instance.
        """
        if self._state.adding and SiteDetail.objects.exists():
            raise ValidationError("There can be only one Site Detail instance")

        return super(SiteDetail, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Site details"


class Subscriber(BaseModel):
    """
    Represents a subscriber to a service or newsletter.

    Attributes:
        email (EmailField): The email address of the subscriber.
        exported (BooleanField): A flag indicating whether the subscriber's details have been exported.

    Methods:
        __str__() -> str:
            Returns the email address of the subscriber as a string representation.
    """

    email = models.EmailField(unique=True)
    exported = models.BooleanField(default=False)

    def __str__(self):
        """
        Return the email address of the subscriber as the string representation.

        Returns:
            str: The email address of the subscriber.
        """
        return self.email


class Message(BaseModel):
    """
    Represents a message sent through the system.

    Attributes:
        name (CharField): The name of the sender.
        email (EmailField): The email address of the sender.
        subject (CharField): The subject of the message.
        text (TextField): The content of the message.
        addressed (BooleanField): A flag indicating whether the message has been addressed.

    Methods:
        __str__() -> str:
            Returns the name of the sender as the string representation.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    text = models.TextField()
    addressed = models.BooleanField(default=False)

    def __str__(self):
        """
        Return the name of the sender as the string representation.

        Returns:
            str: The name of the sender.
        """
        return self.name
