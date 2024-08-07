from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.common.admin import BaseModelAdmin
from .forms import CustomAdminUserChangeForm, CustomAdminUserCreationForm
from .models import User


class Group(DjangoGroup):
    """
    A proxy model for Django's built-in Group model.

    Meta:
        verbose_name (str): The singular name for the model in the admin interface.
        verbose_name_plural (str): The plural name for the model in the admin interface.
        proxy (bool): Indicates that this model is a proxy model.
    """

    class Meta:
        verbose_name = "group"
        verbose_name_plural = "groups"
        proxy = True


class GroupAdmin(BaseGroupAdmin):
    """
    The admin interface for the Group model.
    """

    pass


class UserAdmin(BaseModelAdmin, BaseUserAdmin):
    """
    The admin interface for the User model.

    Attributes:
        ordering (list): The default ordering for the user list view.
        add_form (CustomAdminUserCreationForm): The form used to create new users.
        form (CustomAdminUserChangeForm): The form used to change existing users.
        model (User): The model associated with this admin interface.
        list_display (list): The fields displayed in the user list view.
        list_display_links (list): The fields that link to the user detail view.
        list_filter (list): The fields available for filtering in the user list view.
        fieldsets (tuple): The fieldsets for displaying user information in the detail view.
        add_fieldsets (tuple): The fieldsets for adding a new user in the admin interface.
        search_fields (list): The fields available for searching in the user list view.
    """

    ordering = ["email"]
    add_form = CustomAdminUserCreationForm
    form = CustomAdminUserChangeForm
    model = User

    list_display = [
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    ]

    list_display_links = ["id", "email"]
    list_filter = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    ]
    fieldsets = (
        (
            _("Login Credentials"),
            {"fields": ("email", "password")},
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                    "avatar_url",
                    "account_type",
                )
            },
        ),
        (
            _("Permissions and Groups"),
            {
                "fields": (
                    "is_active",
                    "is_deleted",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important Dates"),
            {"fields": ("last_login", "deleted_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ("avatar_url",)

    def get_readonly_fields(self, request, obj=None):
        """
        Get the readonly fields for the admin form based on the user's permissions.

        Args:
            request (HttpRequest): The current request object.
            obj (Model, optional): The object being edited. Defaults to None.

        Returns:
            list: A list of readonly fields.
        """
        if not request.user.is_superuser:
            readonly_fields = [
                "groups",
                "user_permissions",
                "is_staff",
                "is_superuser",
                "is_active",
            ]
            return readonly_fields
        return self.readonly_fields

    def avatar_url(self, obj):
        return mark_safe(f"<a href='{obj.avatar_url}'>{obj.avatar_url}</a>")


# Register the User and Group models with the admin site.
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(DjangoGroup)
