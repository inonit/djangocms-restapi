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
    API Endpoint which calls the ``{% show_menu %}`` tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument
    list which will be passed to the template tag.

      ``start_level``     Specify from which level the navigation should be rendered.
      ``end_level``       Specify from which level the navigation should stop rendering.
      ``extra_inactive``  Specifies how many levels of navigation should be displayed.
                          if a node is not a direct ancestor or descendant of the current
                          active node.
      ``extra_active``    Specifies how many levels of descendants of the currently active
                          node that should be displayed.
      ``namespace``       The namespace of the menu. If blank, all namespaces will be used.
      ``current_page``    URL for the page that should be considered the `current_page`
                          when rendering the context.
    """

    serializer_class = NavigationNodeSerializer

    def render_context(self, context):
        """
        Render and return the context
        """
        args = ("{start_level} {end_level} {extra_inactive} "
                "{extra_active} {template} {namespace}").format(
            start_level=self.request.GET.get("start_level", 0),
            end_level=self.request.GET.get("end_level", 100),
            extra_inactive=self.request.GET.get("extra_inactive", 0),
            extra_active=self.request.GET.get("extra_active", 1000),
            template='"menu/menu.html"',
            namespace='"%s"' % self.request.GET.get("namespace", ""),
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
    API Endpoint which calls the ``{% show_menu_below_id %}`` tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument
    list which will be passed to the template tag.

      ``root_id``         Specify the ID of the root node.
      ``start_level``     Specify from which level the navigation should be rendered.
      ``end_level``       Specify from which level the navigation should stop rendering.
      ``extra_inactive``  Specifies how many levels of navigation should be displayed.
                          if a node is not a direct ancestor or descendant of the current
                          active node.
      ``extra_active``    Specifies how many levels of descendants of the currently active
                          node that should be displayed.
      ``namespace``       The namespace of the menu. If blank, all namespaces will be used.
      ``current_page``    URL for the page that should be considered the `current_page`
                          when rendering the context.
    """
    def render_context(self, context):
        """
        Render and return the context
        """
        args = ("{root_id} {start_level} {end_level} {extra_inactive} "
                "{extra_active} {template} {namespace}").format(
            root_id='"%s"' % self.request.GET.get("root_id", ""),
            start_level=self.request.GET.get("start_level", 0),
            end_level=self.request.GET.get("end_level", 100),
            extra_inactive=self.request.GET.get("extra_inactive", 0),
            extra_active=self.request.GET.get("extra_active", 1000),
            template='"menu/menu.html"',
            namespace='"%s"' % self.request.GET.get("namespace", "")
        )
        template = Template(
            "".join(("{% load menu_tags %}{% show_menu_below_id ", args, " %}"))
        )
        template.render(context)
        return context


class ShowSubMenuViewSet(ShowMenuViewSet):
    """
    API Endpoint which calls the ``{% show_sub_menu %}`` tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument
    list which will be passed to the template tag.

      ``levels``        Specify how many levels deep the sub menu should be rendered.
      ``root_level``    Specifies at what level (if any) the sub menu should have its root.
      ``nephews``       Specifies how many levels of nephews (children of siblings) that
                        should be displayed.
      ``current_page``  URL for the page that should be considered the `current_page`
                        when rendering the context.
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
    """
    API Endpoint which calls the ``{% show_breadcrumb %}`` tag and returns
    a serialized list of ``NavigationNodes``.

    The following query parameters will be used to construct the argument list
    which will be passed to the template tag.

      ``start_level``   After which level should the breadcrumb start?
                        ``0`` equals home.
      ``only_visible``  Numeric boolean value(0 = False, 1 = True). To include all
                        pages, use ``only_visible=0``.
      ``current_page``  URL for the page that should be considered the `current_page`
                        when rendering the context.
    """

    def get_queryset(self):
        context = self.render_context(self.get_context(self.request))

        # We don't want nested children in the breadcrumb context.
        # This should be a flat structure.
        for node in context["ancestors"]:
            del node.children

        return context["ancestors"]

    def render_context(self, context):
        """
        Constructs the template tag arguments and render it.
        Returns the context.
        """
        args = "{start_level}".format(
            start_level=self.request.GET.get("start_level", 0)
        )
        template = Template(
            "".join(("{% load menu_tags %}{% show_breadcrumb ", args, " %}"))
        )
        template.render(context)
        return context
