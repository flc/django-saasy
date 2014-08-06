from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import Field

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    is_canceled = Field(source="is_canceled")

    class Meta:
        model = Subscription
        exclude = ("id", "user")

