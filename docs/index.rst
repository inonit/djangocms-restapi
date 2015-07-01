
Django CMS REST API
===================

Contents:

.. toctree::
    :maxdepth: 2

    menu/index


About
=====

This project aims to expose Django CMS functionality through a REST API in order to
build and extend features.

Installation
============

.. code-block:: none

    $ pip install -e git+https://github.com/inonit/djangocms-restapi.git#djangocms-restapi



**settings.py**

.. code-block:: python

    INSTALLED_APPS = (
        ...
        djangocms_restapi
        ...
    )


**urls.py**

.. code-block:: python

    urlpatterns = patterns(
        '',
        url(r'^/api/cms/', include('djangocms_restapi.urls'))
    )

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

