# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.template import Template
from django.template.context import Context
from django.utils.six.moves.urllib.parse import unquote
from rest_framework.response import Response

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from .serializers import NavigationNodeSerializer


class ShowMenuViewSet(GenericViewSet):
    """
    API Endpoint which calls the {% show_menu %} tag and returns
    a serialized list of ``NavigationNodes``.

    start_level
    end_level
    extra_inactive
    extra_active

    TODO: Add support for the following arguments
        - namespace
        - root_id
        - next_page_id
    """

    serializer_class = NavigationNodeSerializer

    def get_pages_root(self):
        return unquote(reverse("pages-root"))

    def get_context(self, path=None, page=None):
        """
        Returns the context which will be used for rendering
        the template tag.
        """

        if not path:
            path = self.get_pages_root()
        return Context({"request": self.request})

    def render_context(self, context):
        levels = "{start_level} {end_level} {extra_inactive} {extra_active}".format(
            start_level=self.request.GET.get("start_level", 0),
            end_level=self.request.GET.get("end_level", 100),
            extra_inactive=self.request.GET.get("extra_inactive", 0),
            extra_active=self.request.GET.get("extra_active", 100)
        )
        template = Template(
            "".join(("{% load menu_tags %}{% show_menu ", levels, "%}"))
        )
        template.render(context)
        return context

    def get_queryset(self):
        """
        Retrieve the list of menu items for the menu.
        """
        context = self.render_context(self.get_context())
        return context["children"]

    def list(self, request, *args, **kwargs):
        """
        Serialize and return the queryset. The menu list
        are never paginated.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ShowMenuBelowIdViewSet(ListModelMixin, GenericViewSet):
    pass


class ShowSubMenuViewSet(ListModelMixin, GenericViewSet):
    pass


class ShowBreadcrumbViewSet(ListModelMixin, GenericViewSet):
    pass
