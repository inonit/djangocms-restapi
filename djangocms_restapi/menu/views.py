# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.template import Template
from django.template.context import Context
from rest_framework.response import Response

from cms.models import Page

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from .serializers import NavigationNodeSerializer


class ShowMenuViewSet(GenericViewSet):
    """
    API Endpoint which calls the {% show_menu %} tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the arguments
    list which will be passed to the {% show_menu %} tag.

    ``start_level``     Specify from which level the navigation should be rendered.
    ``end_level``       Specify from which level the navigation should stop rendering.
    ``extra_inactive``  Specifies how many levels of navigation should be displayed.
                        if a node is not a direct ancestor or descendant of the current
                        active node.
    ``extra_active``    Specifies how many levels of descendants of the currently active
                        node that should be displayed.
    ``namespace``       The namespace of the menu. If blank, all namespaces will be used.
    ``root_id``         Specify the ID of the root node.
    """

    serializer_class = NavigationNodeSerializer

    def get_context(self):
        """
        Returns the context which will be used for rendering
        the template tag.
        """
        context = {"request": self.request}
        return Context(context)

    def render_context(self, context):
        """
        Constructs the template tag arguments and render it.
        Returns the context.
        """
        args = ("{start_level} {end_level} {extra_inactive} {extra_active} "
                "{template} {namespace} {root_id}").format(
            start_level=self.request.GET.get("start_level", 0),
            end_level=self.request.GET.get("end_level", 100),
            extra_inactive=self.request.GET.get("extra_inactive", 0),
            extra_active=self.request.GET.get("extra_active", 1000),
            template='"menu/menu.html"',
            namespace='"%s"' % self.request.GET.get("namespace", ""),
            root_id='"%s"' % self.request.GET.get("root_id", "")
        )
        template = Template(
            "".join(("{% load menu_tags %}{% show_menu ", args, " %}"))
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
