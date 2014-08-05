import urllib
import urlparse

from . import settings as app_settings


def encode_dict(data):
    return dict([
        (key, val.encode('utf-8')) for key, val in data.items()
        if isinstance(val, basestring)
        ])


def get_order_page_url(product_path, data=None):
    if not data:
        data = {}

    if app_settings.TEST_MODE:
        data['mode'] = 'test'

    url = 'https://sites.fastspring.com/%s/instant/%s' % (
        app_settings.COMPANY,
        product_path,
    )
    return '%s?%s' % (
        url,
        urllib.urlencode(encode_dict(data)),
    )
