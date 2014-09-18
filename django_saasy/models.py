import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from shortuuidfield import ShortUUIDField

import fastspring

from . import settings as app_settings
from .utils import get_order_page_url


logger = logging.getLogger(__name__)
fastspring_api = fastspring.FastSpringAPI(
    username=app_settings.USERNAME,
    password=app_settings.PASSWORD,
    company=app_settings.COMPANY,
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="saasy_subscription",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        )
    referrer = ShortUUIDField(
        unique=True,
        db_index=True,
        )
    # subscription reference
    reference = models.TextField(blank=True)
    status = models.TextField(blank=True)
    status_changed = models.DateTimeField(null=True, blank=True)
    status_reason = models.TextField(blank=True)
    next_period_date = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    product_name = models.TextField(blank=True)
    is_cancelable = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    # Customer URL that can be used to Update Payment Method
    # or to Cancel Subscription
    customer_url = models.TextField(blank=True)

    def get_order_page_url_params(self):
        # https://support.fastspring.com/entries/20953842
        # XXX
        # Quote from the docs: "To use the pre-fill functionality, we require that you
        # at least pass contact_fname and contact_lname. In other words, you cannot
        # pre-fill a customer's email address without pre-filling the first and last name.
        # this is why we pass " " as first and last name
        data = {
            'referrer': self.referrer,
            'contact_fname': self.user.first_name or " ",
            'contact_lname': self.user.last_name or " ",
            'contact_email': self.user.email,
        }
        return data

    def get_order_page_url(self, product_path):
        data = self.get_order_page_url_params()
        return get_order_page_url(product_path, data=data)

    @classmethod
    def get_or_create_from_user(cls, user):
        obj, created = cls.objects.get_or_create(user=user)
        return obj, created

    def fetch_from_api(self):
        if not self.reference:
            return
        return fastspring_api.get_subscription(self.reference)

    @staticmethod
    def _parse_date(date):
        # XXX really FastSpring? come on!
        if date:
            if date.endswith("Z"):
                date = date[:-1]
        return date

    def update_from_data(self, data):
        if self.status == "active":
            if ((self.reference and data['reference'] != self.reference) or
                data['referrer'] != self.referrer):
                # this should not happen at all
                raise ValueError("Subscription reference or referrer mismatch")

        self.reference = data['reference']
        self.customer_url = data['customerUrl']
        self.status = data['status']
        self.status_changed = data.get('statusChanged')
        self.status_reason = data.get('statusReason', '')
        self.next_period_date = self._parse_date(data.get('nextPeriodDate'))
        self.end = self._parse_date(data.get('end'))
        self.product_name = data['productName']
        self.is_cancelable = data['cancelable'] == 'true'
        self.is_test = data.get('test') == 'true'
        self.save()

    def update_from_api(self):
        data = self.fetch_from_api()
        if data:
            data = data['subscription']
            return self.update_from_data(data)

    @property
    def is_canceled(self):
        return self.end is not None and self.status_reason == "canceled"

    def cancel(self):
        return fastspring_api.cancel_subscription(self.reference)

    def reactivate(self):
        if self.is_canceled:
            data = fastspring_api.update_subscription(
                self.reference,
                {'no-end-date': None},
                )
            data = data['subscription']
            logger.debug('subscription reactivated: %s', data)
            self.update_from_data(data)
            return data
    uncancel = reactivate

    def change(self, plan_code):
        data = {}
        data['productPath'] = '/' + plan_code
        data['proration'] = True
        return fastspring_api.update_subscription(self.reference, data)
