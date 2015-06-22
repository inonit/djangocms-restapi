
REST API for Django CMS Based on Django REST Framework
======================================================


Installation
============

Not yet released


Setup
=====


In your ``urls.py`` file, add the following entry to include all the api's.

    #
    # urls.py
    #
    
    patterns = urlpatterns(
        "",
        ...
        url(r"^/cms-api/", include("djangocms_restapi.urls"),
        ...
    )


