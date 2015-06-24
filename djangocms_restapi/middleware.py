# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
from cms.middleware.page import get_page


class CurrentPageCookieMiddleWare(object):
    """
    Inserts the current page in the session
    """

    def process_response(self, request, response):
        current_page = getattr(request, "current_page", get_page(request))
        current_page = current_page.get_absolute_url()

        if hasattr(request, "session"):
            session_page = request.session.get("current_page", None)
            if session_page and not session_page == current_page:
                request.session["current_language"] = current_page
                request.session.save()

        if "current_page" in request.COOKIES and request.COOKIES["current_page"] == current_page:
            return response

        max_age = 365 * 24 * 60 * 60  # 10 years
        expires = datetime.utcnow() + timedelta(seconds=max_age)
        response.set_cookie("current_page", current_page, expires=expires)
        return response
