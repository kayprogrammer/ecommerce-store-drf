class GuestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Setting guest
        response = self.get_response(request)
        if hasattr(request, "guest_id"):
            response.data["guest_id"] = request.guest_id
        return response
