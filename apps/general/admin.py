from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from import_export import resources
from import_export.admin import ExportActionMixin
from .models import Message, SiteDetail, Subscriber


class SiteDetailAdmin(admin.ModelAdmin):
    """
    Admin interface customization for the SiteDetail model.

    This admin class is designed to handle the SiteDetail model with specific
    configurations:

    Fieldsets:
        - General: Includes fields for `name`, `email`, `phone`, and `address`.
        - Social: Includes fields for `fb` (Facebook), `tw` (Twitter), `wh` (Whatsapp), and `ig` (Instagram).

    Permissions:
        - Add Permission: Disabled (no new instances can be added).
        - Delete Permission: Disabled (no instances can be deleted).

    Methods:
        has_add_permission(request): Disables the ability to add new SiteDetail instances.
        has_delete_permission(request, obj=None): Disables the ability to delete existing SiteDetail instances.
        changelist_view(request, extra_context=None): Redirects to the change form of the existing SiteDetail instance.
    """

    fieldsets = (
        ("General", {"fields": ["name", "email", "phone", "address"]}),
        ("Social", {"fields": ["fb", "tw", "wh", "ig"]}),
    )

    def has_add_permission(self, request):
        """
        Disables the ability to add new SiteDetail instances.

        Args:
            request (HttpRequest): The request object.

        Returns:
            bool: False, preventing the addition of new instances.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disables the ability to delete existing SiteDetail instances.

        Args:
            request (HttpRequest): The request object.
            obj (SiteDetail, optional): The specific instance being deleted.

        Returns:
            bool: False, preventing the deletion of instances.
        """
        return False

    def changelist_view(self, request, extra_context=None):
        """
        Redirects to the change form of the existing SiteDetail instance.

        If no instance exists, a new one is created. Redirects to the change
        form of the instance using its ID.

        Args:
            request (HttpRequest): The request object.
            extra_context (dict, optional): Additional context for the template.

        Returns:
            HttpResponseRedirect: Redirects to the change form of the SiteDetail instance.
        """
        obj, created = self.model.objects.get_or_create()
        return HttpResponseRedirect(
            reverse(
                "admin:%s_%s_change"
                % (self.model._meta.app_label, self.model._meta.model_name),
                args=(obj.id,),
            )
        )


class SubscriberResource(resources.ModelResource):
    class Meta:
        model = Subscriber
        fields = ("email",)


class SubscriberAdmin(ExportActionMixin, admin.ModelAdmin):
    """
    Admin interface for managing `Subscriber` model instances.

    Attributes:
        list_display (list): Fields to display in the list view of subscribers.
        list_filter (list): Fields to filter the list of subscribers.
        resource_class (SubscriberResource): Resource class for exporting subscriber data.

    Methods:
        export_action(request, *args, **kwargs):
            Overrides the default export action to mark subscribers as exported after export.
    """

    list_display = ["email", "exported", "created_at"]
    list_filter = list_display
    resource_class = SubscriberResource

    def export_action(self, request, *args, **kwargs):
        """
        Handles the export action, marking subscribers as exported after export.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The response from the super class's export action method.
        """
        response = super().export_action(request, *args, **kwargs)
        qs = self.get_export_queryset(request)
        qs.update(exported=True)
        return response


class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing `Message` model instances.

    Attributes:
        list_display (tuple): Fields to display in the list view of messages.
        list_filter (tuple): Fields to filter the list of messages.
    """

    list_display = ("name", "email", "subject", "addressed")
    list_filter = list_display


admin.site.register(SiteDetail, SiteDetailAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Message, MessageAdmin)
