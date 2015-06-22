# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url
from rest_framework import routers
from .views import ShowMenuViewSet, ShowMenuBelowIdViewSet, ShowSubMenuViewSet, ShowBreadcrumbViewSet


router = routers.DefaultRouter()
router.register(r"show-menu", ShowMenuViewSet, base_name="show-menu")
router.register(r"show-menu-below-id", ShowMenuBelowIdViewSet, base_name="show-menu-below-id")
router.register(r"show-submenu", ShowSubMenuViewSet, base_name="show-submenu")
router.register(r"show-breadcrumb", ShowBreadcrumbViewSet, base_name="show-breadcrumb")


urlpatterns = patterns(
    "",
    url(r"^", include(router.urls))
)
