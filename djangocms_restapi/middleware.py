# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
from cms.middleware.page import get_page


class CurrentPageCookieMiddleWare(object):
    """
    Sets the `current_page` in the Cookie Store.
    """

    def process_response(self, request, response):
        current_page = getattr(request, "current_page", get_page(request))
        if current_page:
            # Only update do this if we're on a "cms page"!
            current_page = current_page.get_absolute_url()

            if hasattr(request, "session"):
                session_page = request.session.get("current_page", None)
                if not session_page == current_page:
                    request.session["current_language"] = current_page
                    request.session.save()

            if "current_page" in request.COOKIES and request.COOKIES["current_page"] == current_page:
                return response

            max_age = 365 * 24 * 60 * 60  # 10 years
            expires = datetime.utcnow() + timedelta(seconds=max_age)
            response.set_cookie("current_page", current_page, expires=expires)
            return response

        return response
