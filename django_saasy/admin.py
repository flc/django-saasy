from django.contrib import admin

from . import models


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_name', 'referrer', 'status', 'status_reason', 'next_period_date', 'is_test')
    search_fields = ('=user__id', '=referrer', '=reference')
    list_filter = ('status', 'product_name', 'status_reason', 'is_test', )
    raw_id_fields = ('user',)


admin.site.register(models.Subscription, SubscriptionAdmin)
