from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns("",
    url(r"^notification/$", views.notification, name="notification"),
)
