from rest_framework.renderers import JSONRenderer

from apps.accounts.models import GuestUser


class GuestIDRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context.get("request")

        # Modify the data if the user is a GuestUser
        if isinstance(request.user, GuestUser) and isinstance(data, dict):
            data["guest_id"] = str(request.user)

        return super().render(data, accepted_media_type, renderer_context)
