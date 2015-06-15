# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url


urlpatterns = patterns(
    "",
    url(r"^menu/", include("cms_restapi.menu.urls"))
)
