
REST API for Django CMS Based on Django REST Framework
======================================================

![alt text](https://readthedocs.org/projects/djangocms-restapi/badge/?version=latest "Docs build status")
![alt text](https://travis-ci.org/inonit/djangocms-restapi.svg "Build status")


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


