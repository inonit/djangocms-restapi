# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.template import Template
from django.template.context import Context

from rest_framework.request import clone_request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cms.middleware.page import CurrentPageMiddleware

from .serializers import NavigationNodeSerializer


class CurrentPageAPIContextMixin(CurrentPageMiddleware):
    """
    Returns a Context object with a clone of the HttpRequest.
    The request clone is ran through the ``CurrentPageMiddleware``
    before returned.
    """
    def __init__(self, *args, **kwargs):
        super(CurrentPageAPIContextMixin, self).__init__(*args, **kwargs)
        self.context = Context()

    def get_context(self, request):
        request = clone_request(request, request.method)

        if "current_page" in request.GET:
            request.path = request.path_info = request.GET["current_page"]

        self.process_request(request)
        self.context["request"] = request
        return self.context


class ShowMenuViewSet(CurrentPageAPIContextMixin, GenericViewSet):
    """
    API Endpoint which calls the {% show_menu %} tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument
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

    def render_context(self, context):
        """
        Render and return the context
        """
        args = ("{start_level} {end_level} {extra_inactive} {extra_active} "
                "{template} {namespace} {root_id}").format(
            start_level=context["request"].GET.get("start_level", 0),
            end_level=context["request"].GET.get("end_level", 100),
            extra_inactive=context["request"].GET.get("extra_inactive", 0),
            extra_active=context["request"].GET.get("extra_active", 1000),
            template='"menu/menu.html"',
            namespace='"%s"' % context["request"].GET.get("namespace", ""),
            root_id='"%s"' % context["request"].GET.get("root_id", "")
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
        context = self.render_context(self.get_context(self.request))
        return context["children"]

    def list(self, request, *args, **kwargs):
        """
        Serialize and return the queryset. The menu list
        are never paginated.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ShowMenuBelowIdViewSet(ShowMenuViewSet):
    """
    API Endpoint which calls the {% show_menu_below_id %} tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument
    list which will be passed to the {% show_menu_below_id %} tag.

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
    pass


class ShowSubMenuViewSet(ShowMenuViewSet):
    """
    API Endpoint which calls the {% show_sub_menu %} tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument
    list which will be passed to the {% show_sub_menu %} tag.

      ``levels``        Specify how many levels deep the sub menu should be rendered.
      ``root_level``    Specifies at what level (if any) the sub menu should have its root.
      ``nephews``       Specifies how many levels of nephews (children of siblings) that
                        should be displayed.
      ``current_page``  Set the ``request.current_page`` for the request. Must be a valid
                        url ie. /home/. This is useful for rendering menu items relative
                        to a specified path.
    """
    def render_context(self, context):
        """
        Constructs the template tag arguments and render it.
        Returns the context.
        """
        args = "{levels} {root_level} {nephews}".format(
            levels=self.request.GET.get("levels", 100),
            root_level=self.request.GET.get("root_level", None),
            nephews=self.request.GET.get("nephews", 100)
        )
        template = Template(
            "".join(("{% load menu_tags %}{% show_sub_menu ", args, " %}"))
        )
        template.render(context)
        return context


class ShowBreadcrumbViewSet(ShowMenuViewSet):
    pass
