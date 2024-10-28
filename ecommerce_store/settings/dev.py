from .base import *
from django.utils.log import DEFAULT_LOGGING
import logging, logging.config

DEBUG = True

logger = logging.getLogger(__name__)

LOG_LEVEL = "INFO"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'drf_spectacular': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'py.warnings': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += [
    "querycount.middleware.QueryCountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.alerts.AlertsPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]
