# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    "",
    url(r"^cms-restapi/", include("djangocms_restapi.urls"))
)
