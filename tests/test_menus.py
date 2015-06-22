# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals


from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib.parse import unquote

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from cms.models import Page
from cms.test_utils.fixtures.menus import ExtendedMenusFixture


PAGES_ROOT = unquote(reverse("pages-root"))
factory = APIRequestFactory(enforce_csrf_checks=False)

class BaseMenuAPITestCase(ExtendedMenusFixture, APITestCase):
    """
    Tree from fixture:
        + P1
        | + P2
        |   + P3
        | + P9
        |   + P10
        |      + P11
        + P4
        | + P5
        + P6 (not in menu)
          + P7
          + P8
    """

    def setUp(self):
        self.create_fixtures()

    def get_page(self, num):
        return Page.objects.public().get(title_set__title='P%s' % num)

    def get_level(self, num):
        return Page.objects.public().filter(depth=num)

    def get_all_pages(self):
        return Page.objects.public()


class ShowMenuViewSetTestCase(BaseMenuAPITestCase):

    def setUp(self):
        super(ShowMenuViewSetTestCase, self).setUp()
        self.url = reverse("show-menu-list")

    def test_show_menu(self):
        response = self.client.get(self.url, data="", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["sibling"], False)
        self.assertEqual(response.data[0]["descendant"], False)
        self.assertEqual(response.data[0]["children"][0]["descendant"], True)
        self.assertEqual(response.data[0]["children"][0]["children"][0]["descendant"], True)
        self.assertEqual(response.data[0]["children"][0]["children"][0]["is_leaf_node"], True)
        self.assertEqual(response.data[0]["url"], PAGES_ROOT)
        self.assertEqual(response.data[0]["attrs"]["auth_required"], False)
        self.assertEqual(response.data[0]["attrs"]["is_home"], True)
        self.assertEqual(response.data[0]["attrs"]["redirect_url"], None)
        self.assertEqual(response.data[0]["attrs"]["reverse_id"], None)
        self.assertEqual(response.data[0]["attrs"]["soft_root"], False)
        self.assertEqual(response.data[0]["attrs"]["visible_for_anonymous"], True)
        self.assertEqual(response.data[0]["attrs"]["visible_for_authenticated"], True)
        self.assertEqual(response.data[1]["sibling"], True)
        self.assertEqual(response.data[1]["url"], self.get_page(4).get_absolute_url())

    def test_show_menu_selected_path(self):
        response = self.client.get(
            self.url,
            data={"current_page": "/p2/"},
            format="json"
        )
        self.assertEqual(response.data[0]["children"][0]["selected"], True)

    def test_show_menu_only_active_tree(self):

        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 100, "extra_inactive": 0, "extra_active": 100},
            format="json"
        )
        self.assertEqual(len(response.data[1]["children"]), 0)
        self.assertEqual(len(response.data[0]["children"]), 2)
        self.assertEqual(len(response.data[0]["children"][0]["children"]), 1)

        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 100, "extra_inactive": 0, "extra_active": 100, "current_page": "/p4/"},
            format="json"
        )
        self.assertEqual(len(response.data[1]["children"]), 1)
        self.assertEqual(len(response.data[0]["children"]), 0)

    def test_show_menu_only_one_active_level(self):
        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 100, "extra_inactive": 0, "extra_active": 1},
            format="json"
        )
        self.assertEqual(len(response.data[1]["children"]), 0)
        self.assertEqual(len(response.data[0]["children"]), 2)
        self.assertEqual(len(response.data[0]["children"][0]["children"]), 0)

    def test_show_menu_only_level_zero(self):
        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 0, "extra_inactive": 0, "extra_active": 0},
            forma="json"
        )
        for node in response.data:
            self.assertEqual(len(node["children"]), 0)

    def test_show_menu_only_level_one(self):
        response = self.client.get(
            self.url,
            data={"start_level": 1, "end_level": 1, "extra_inactive": 100, "extra_active": 100},
            format="json"
        )
        for node in response.data:
            self.assertEqual(len(node["children"]), 0)

    def test_show_menu_only_level_one_active(self):
        response = self.client.get(
            self.url,
            data={"start_level": 1, "end_level": 1, "extra_inactive": 0, "extra_active": 100},
            format="json"
        )
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["descendant"], True)
        self.assertEqual(len(response.data[0]["children"]), 0)

    def test_show_menu_level_zero_and_one(self):
        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 1, "extra_inactive": 100, "extra_active": 100},
            format="json"
        )
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[0]["children"]), 2)
        for node in response.data[0]["children"]:
            self.assertEqual(len(node["children"]), 0)

        self.assertEqual(len(response.data[1]["children"]), 1)
        for node in response.data[1]["children"]:
            self.assertEqual(len(node["children"]), 0)

class ShowMenuBelowIdViewSetTestCase(BaseMenuAPITestCase):

    def setUp(self):
        super(ShowMenuBelowIdViewSetTestCase, self).setUp()
        self.url = reverse("show-menu-below-id-list")


class ShowSubMenuViewSetTestCase(BaseMenuAPITestCase):

    def setUp(self):
        super(ShowSubMenuViewSetTestCase, self).setUp()
        self.url = reverse("show-submenu-list")

    def test_show_submenu(self):
        response = self.client.get(self.url, data="", format="json")
        self.assertEqual(response.data[0]["descendant"], True)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[0]["children"]), 1)
        self.assertEqual(len(response.data[1]["children"]), 1)
        self.assertEqual(len(response.data[1]["children"][0]["children"]), 1)

    def test_show_submenu_only_one_level(self):
        response = self.client.get(self.url, data={"levels": 1}, format="json")
        self.assertEqual(len(response.data), 2)
        for node in response.data:
            self.assertEqual(len(node["children"]), 0)

    def test_show_submenu_current_page(self):
        response = self.client.get(
            self.url,
            data={"levels": 100, "current_page": "/p9/"},
            format="json"
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]["children"]), 1)
        self.assertEqual(response.data[0]["url"], "/p9/p10/")
        self.assertEqual(response.data[0]["children"][0]["url"], "/p9/p10/p11/")
        self.assertEqual(
            response.data[0]["id"],
            response.data[0]["children"][0]["parent_id"]
        )

    def test_show_submenu_root_level_one(self):
        response = self.client.get(
            self.url,
            data={"levels": 2, "root_level": 1, "current_page": "/p9/"},
            format="json"
        )
        self.assertEqual(len(response.data), 2)
        for node in response.data:
            self.assertEqual(len(node["children"]), 1)

        self.assertEqual(response.data[1]["url"], "/p9/")
        self.assertEqual(response.data[1]["selected"], True)
        self.assertEqual(response.data[1]["parent_url"], self.get_page(1).get_absolute_url())

class ShowBreadcrumbViewSetTestCase(BaseMenuAPITestCase):

    def setUp(self):
        super(ShowBreadcrumbViewSetTestCase, self).setUp()
        self.url = reverse("show-breadcrumb-list")

