# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url

from rest_framework import routers
from .views import ShowMenuViewSet


router = routers.DefaultRouter()
router.register(r"show-menu", ShowMenuViewSet, base_name="show-menu")

urlpatterns = patterns(
    "",
    url(r"^", include(router.urls))
)
