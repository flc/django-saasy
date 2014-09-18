import logging
import functools
import hashlib
import json

from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseForbidden
from django.utils.crypto import constant_time_compare

from . import settings as app_settings


logger = logging.getLogger(__name__)


def basic_authentication(fn):
    @functools.wraps(fn)
    def wrapper(request, *args, **kwargs):
        authentication = app_settings.NOTIFICATION_HTTP_AUTHENTICATION

        # If the user has not setup settings.NOTIFICATION_HTTP_AUTHENTICATION then
        # we trust they are doing it at the web server level.
        if authentication is None:
            return fn(request, *args, **kwargs)

        try:
            method, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
        except KeyError:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="Restricted"'
            return response

        try:
            if method.lower() != 'basic':
                raise ValueError()

            if not constant_time_compare(auth.strip().decode('base64'), authentication):
                return HttpResponseForbidden()
        except Exception:
            return HttpResponseBadRequest()

        return fn(request, *args, **kwargs)
    return wrapper


def private_key_validation(fn):
    @functools.wraps(fn)
    def wrapper(request, *args, **kwargs):
        private_keys = app_settings.NOTIFICATION_PRIVATE_KEYS

        try:
            # data = json.loads(request.body)
            # security_data = request.META['HTTP_X_SECURITY_DATA']
            # security_hash = request.META['HTTP_X_SECURITY_HASH']
            data = request.POST
            notification_type = data['notificationType']
            private_key = private_keys[notification_type]
            security_data = data['security_data']
            security_hash = data['security_hash']
            if hashlib.md5(security_data + private_key).hexdigest() != security_hash:
                # security check failed
                logger.info("Security check failed.")
                return HttpResponseBadRequest()
        except Exception as e:
            logger.exception(e)
            return HttpResponseBadRequest()

        return fn(request, *args, **kwargs)
    return wrapper
