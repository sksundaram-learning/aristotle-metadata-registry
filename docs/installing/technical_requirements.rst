Technical requirements
======================

The Aristotle Metadata Registry is built on the django framework which supports a wide range of
operating systems and databases. While Aristotle-MDR should support most of these
only a small set of configurations have been thoroughly tested on the
`Travis-CI continuous <https://travis-ci.org/aristotle-mdr/aristotle-metadata-registry/>`_
integration system as "supported infrastucture".

Operating system support
------------------------

* Ubuntu Linux 12.04 LTS

Travis-CI does not yet have containerised support for the Ubuntu 14.04 or 16.04
long-term support releases.

Python
------
* Python 2.7

Some modules are incompatible with Python 3 (support coming soon).

Django
------

* Django version 1.8 LTS

Database support
----------------

* SQLite
* Postgres

MySQL has a number of small issues in the test suite (full coverage coming soon).

Search index support
--------------------

* Elasticsearch 2.4+
* Whoosh