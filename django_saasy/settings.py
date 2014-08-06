from django.conf import settings


COMPANY = settings.SAASY_COMPANY
USERNAME = settings.SAASY_USERNAME
PASSWORD = settings.SAASY_PASSWORD
NOTIFICATION_PRIVATE_KEYS = getattr(settings, "SAASY_NOTIFICATION_PRIVATE_KEYS", {})
# The username & password used to authorise Recurly's
# webhook. In the format "username:password"
NOTIFICATION_HTTP_AUTHENTICATION = \
    getattr(settings, 'SAASY_NOTIFICATION_HTTP_AUTHENTICATION', None)
TEST_MODE = getattr(settings, 'SAASY_TEST_MODE', True)
NOTIFICATION_LOG_ENABLED = getattr(settings, 'SAASY_NOTIFICATION_LOG_ENABLED', True)
