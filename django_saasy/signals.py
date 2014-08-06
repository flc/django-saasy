from django.dispatch import Signal


# signals for fastspring notifications
subscription_activated = Signal(providing_args=('data',))
subscription_changed = Signal(providing_args=('data',))
subscription_deactivated = Signal(providing_args=('data',))
subscription_payment_failed = Signal(providing_args=('data',))
order_completed = Signal(providing_args=('data',))
