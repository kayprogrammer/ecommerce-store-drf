from rest_framework.permissions import BasePermission
from apps.accounts.auth import Authentication
from apps.accounts.models import GuestUser
from apps.common.exceptions import ErrorCode, RequestError


def get_user(bearer):
    user = Authentication.decodeAuthorization(bearer)
    if not user:
        raise RequestError(
            err_code=ErrorCode.INVALID_TOKEN,
            err_msg="Access Token is Invalid or Expired!",
            status_code=401,
        )
    if not user.is_active:
        raise RequestError(
            err_code=ErrorCode.DEACTIVATED_ACCOUNT,
            err_msg="This account has been deactivated!",
            status_code=401,
        )
    return user


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        http_auth = request.META.get("HTTP_AUTHORIZATION")
        if not http_auth:
            raise RequestError(
                err_code=ErrorCode.INVALID_AUTH,
                err_msg="Auth Bearer not provided!",
                status_code=401,
            )
        user = get_user(http_auth)
        request.user = user
        if request.user and request.user.is_authenticated:
            return True
        return False


class IsAuthenticatedOrGuestCustom(BasePermission):
    def has_permission(self, request, view):
        http_auth = request.META.get("HTTP_AUTHORIZATION")
        guest_id = request.META.get("HTTP_GUEST_USER_ID")
        if http_auth:
            user = get_user(http_auth)
            request.user = user
        else:
            guest = GuestUser.objects.get_or_none(id=guest_id)
            if not guest:
                guest = GuestUser.objects.create()
            request.user = guest
        return True


def set_dict_attr(obj, data):
    for attr, value in data.items():
        setattr(obj, attr, value)
    return obj
