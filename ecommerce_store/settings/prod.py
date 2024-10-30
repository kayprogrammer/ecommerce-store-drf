from .base import *

DEBUG = False
# For ssl conf
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "drf_spectacular": {
            "handlers": ["console"],
            "level": "ERROR",  # Change this to ERROR to hide warnings
            "propagate": True,
        },
    },
}
