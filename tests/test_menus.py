# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals


from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib.parse import unquote

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from cms.models import Page
from cms.test_utils.fixtures.menus import ExtendedMenusFixture, SoftrootFixture


PAGES_ROOT = unquote(reverse("pages-root"))
factory = APIRequestFactory(enforce_csrf_checks=False)

class BaseAPITestCase(APITestCase):

    def setUp(self):
        self.create_fixtures()

    def tearDown(self):
        Page.objects.public().delete()

    def get_page(self, slug):
        return Page.objects.public().get(title_set__slug=slug)

    def get_level(self, num):
        return Page.objects.public().filter(depth=num)

    def get_all_pages(self):
        return Page.objects.public()


class ShowMenuViewSetTestCase(ExtendedMenusFixture, BaseAPITestCase):
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
        self.assertEqual(response.data[1]["url"], self.get_page("p4").get_absolute_url())

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


class SoftRootShowMenuViewSetTestCase(SoftrootFixture, BaseAPITestCase):
    """
    Tree from fixture:
    + top
    |  + root (SOFTROOT)
    |    + aaa
    |      + 111
    |        + ccc
    |          + ddd
    |      + 222
    |    + bbb
    |      + 333
    |      + 444

    """

    def setUp(self):
        super(SoftRootShowMenuViewSetTestCase, self).setUp()
        self.url = reverse("show-menu-list")

    def test_show_menu_no_softroot(self):
        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 100, "extra_inactive": 0, "extra_active": 100,
                  "current_page": self.get_page("aaa").get_absolute_url()},
            format="json"
        )

        self.assertEqual(response.data[0]["title"], "top")
        self.assertEqual(response.data[0]["children"][0]["attrs"]["soft_root"], False)
        self.assertEqual(response.data[0]["children"][0]["children"][0]["selected"], True)

    def test_show_menu_with_softroot(self):

        root = self.get_page("root")
        root.soft_root = True
        root.save()

        response = self.client.get(
            self.url,
            data={"start_level": 0, "end_level": 100, "extra_inactive": 0, "extra_active": 100,
                  "current_page": self.get_page("aaa").get_absolute_url()},
            format="json"
        )

        self.assertEqual(response.data[0]["title"], "root")
        self.assertEqual(response.data[0]["attrs"]["soft_root"], True)
        self.assertEqual(response.data[0]["children"][0]["selected"], True)


class ShowMenuBelowIdViewSetTestCase(ExtendedMenusFixture, BaseAPITestCase):
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
        super(ShowMenuBelowIdViewSetTestCase, self).setUp()
        self.url = reverse("show-menu-below-id-list")

    def test_show_menu_below_id_not_in_navigation(self):
        p6 = self.get_page("p6")
        p6.reverse_id = "p6"
        p6.save()

        response = self.client.get(
            self.url,
            data={"root_id": "p6", "start_level": 0, "end_level": 100, "extra_inactive": 100,
                  "extra_active": 100, "current_page": self.get_page("p7").get_absolute_url()},
            format="json"
        )

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "P7")
        self.assertEqual(response.data[0]["parent_id"], self.get_page("p6").pk)

    def test_show_menu_below_id_ignore_softroot(self):
        p1 = self.get_page("p1")
        p1.reverse_id = "p1"
        p1.save()

        p9 = self.get_page("p9")
        p9.soft_root = True
        p9.save()

        response = self.client.get(
            self.url,
            data={"root_id": "p1", "start_level": 0, "end_level": 100, "extra_inactive": 100,
                  "extra_active": 100, "current_page": self.get_page("p10").get_absolute_url()},
            format="json"
        )

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["url"], self.get_page("p2").get_absolute_url())
        self.assertEqual(response.data[1]["url"], self.get_page("p9").get_absolute_url())
        self.assertEqual(response.data[1]["children"][0]["selected"], True)

class ShowSubMenuViewSetTestCase(ExtendedMenusFixture, BaseAPITestCase):
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
        self.assertEqual(response.data[1]["parent_url"], self.get_page("p1").get_absolute_url())

    def test_show_submenu_nephews(self):
        response = self.client.get(
            self.url,
            data={"levels": 100, "root_level": 1, "nephews": 1, "current_page": "/p2/"},
            format="json"
        )
        self.assertEqual(response.data[0]["url"], "/p2/")
        self.assertEqual(response.data[0]["selected"], True)

        # Should include P10 but not P11
        self.assertEqual(len(response.data[1]["children"]), 1)
        self.assertEqual(len(response.data[1]["children"][0]["children"]), 0)

        response = self.client.get(
            self.url,
            data={"levels": 100, "root_level": 1, "current_page": "/p2/"},
            format="json"
        )
        # Should include both P10 and P11
        self.assertEqual(len(response.data[1]["children"]), 1)
        self.assertEqual(len(response.data[1]["children"][0]["children"]), 1)

    def test_show_submenu_nephew_no_limit(self):
        response = self.client.get(
            self.url,
            data={"levels": 100, "nephews": 100, "current_page": "/"},
            format="json"
        )
        self.assertEqual(len(response.data), 2)

class ShowBreadcrumbViewSetTestCase(ExtendedMenusFixture, BaseAPITestCase):
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
        super(ShowBreadcrumbViewSetTestCase, self).setUp()
        self.url = reverse("show-breadcrumb-list")

    def test_show_breadcrumb(self):
        response = self.client.get(
            self.url,
            data={"current_page": self.get_page("p3").get_absolute_url()},
            format="json"
        )
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["parent_url"], None)
        self.assertEqual(response.data[1]["parent_url"], self.get_page("p1").get_absolute_url())
        self.assertEqual(response.data[2]["parent_url"], self.get_page("p2").get_absolute_url())

    def test_show_breadcrumb_start_level(self):
        response = self.client.get(
            self.url,
            data={"current_page": self.get_page("p3").get_absolute_url(),
                  "start_level": 1},
            format="json"
        )
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["parent_url"], self.get_page("p1").get_absolute_url())
        self.assertEqual(response.data[1]["parent_url"], self.get_page("p2").get_absolute_url())
