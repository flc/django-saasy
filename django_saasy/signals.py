from django.dispatch import Signal


# signals for fastspring notifications
subscription_activated = Signal(providing_args=('data', 'raw_data'))
subscription_changed = Signal(providing_args=('data', 'raw_data'))
subscription_deactivated = Signal(providing_args=('data', 'raw_data'))
subscription_payment_failed = Signal(providing_args=('data', 'raw_data'))
order_completed = Signal(providing_args=('data', 'raw_data'))
order_completed_per_product = Signal(providing_args=('data', 'raw_data'))
