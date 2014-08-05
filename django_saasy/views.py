import logging
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .decorators import basic_authentication, private_key_validation
from .models import Subscription, fastspring_api
from . import signals


logger = logging.getLogger(__name__)


@csrf_exempt
@basic_authentication
@private_key_validation
@require_POST
def notification(request):
    # big try catch because we don't want to send back any
    # technical error response with all our settings if we happen to
    # test the webhooks with DEBUG=True
    try:
        # data = json.loads(request.body)
        data = request.POST
        try:
            _type = data['notificationType']
            logger.info("FastSpring notification: %s", _type)
            signal = getattr(signals, _type)
        except AttributeError:
            return HttpResponseBadRequest("Unrecognized notification type.")

        # subscription = fastspring_api.get_subscription(data['reference'])
        subscription = fastspring_api.get_subscription(data['SubscriptionReference'])
        subscription = subscription['subscription']
        signal.send(sender=request, data=subscription)
    except Exception as e:
        if settings.DEBUG:
            logger.exception(e)
            return HttpResponse(status=500)
        raise

    return HttpResponse()


if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import authentication, permissions
    from rest_framework import status


    class OrderPageDataView(APIView):
        allowed_methods = ['post']

        permission_classes = (permissions.IsAuthenticated, )

        def post(self, request, format=None):
            # we use POST because it's possible that there is no
            # associated Account object for the user yet and we
            # need to create it and generate a unique account_code
            # for it
            try:
                plan_code = request.DATA['plan_code']
            except KeyError:
                return Response(
                    {'plan_code': 'Plan code is missing'},
                    status=status.HTTP_400_BAD_REQUEST,
                    )

            user = request.user
            subscription, created = Subscription.get_or_create_from_user(user)
            return Response({
                'url': subscription.get_order_page_url(plan_code)
                })


    class CustomerUrlView(APIView):

        def get(self, request, format=None):
            user = request.user
            url = None
            try:
                subscription = Subscription.objects.filter(user=request.user)[0]
            except IndexError:
                url = None
            else:
                url = subscription.customer_url
            return Response({
                'url': url
                })

