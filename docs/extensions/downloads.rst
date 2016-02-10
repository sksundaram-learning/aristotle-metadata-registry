Adding new download formats
===========================

While the Aristotle-MDR framework includes PDF download capability, it may be
desired to download metadata stored within a registry in a variety of download
formats. Rather than include these within the Aristotle-MDR core codebase,
additional download formats can be developed included via the download API.

Creating a download module
--------------------------------------------

A download module is just a specialised Django app that includes a specific set
of files for generating downloads. The files required in your app are:

* ``__init__.py`` - to declare the app as a python module
* ``downloader.py`` - for defining your main download method

Other modules can be written, for example a download module may define models for
recording a number of times an item is downloaded.

Writing a ``downloader.download`` method
----------------------------------------
Your ``downloader.py`` file must contain a method with the following signature::

    def download(request,downloadType,item):

This is called from Aristotle-MDR when it catches a download type that has been
registered for this module. The arguments are:

* ``request`` - the `request object <https://docs.djangoproject.com/en/stable/ref/request-response/>`_
  that was used to call the download view. The current user trying to download the
  item can be gotten by calling ``request.user``.

* ``downloadType`` - a short string used to differentiate different download formats

* ``item`` - the item to be downloaded, as retrieved from the database.

**Note:** If a download method is called the user has been verified to have
permissions to view the requested item only. Permissions for other items will
have to be checked within the download method.

For an example of how to handle multiple download formats in a single module,
review the ``aristotle_mdr.downloader`` module which provides downloads in the
PDF and CSV format for various content types which is linked below:

.. automodule:: aristotle_mdr.downloader
   :members: download


How the ``download`` view works
-------------------------------

.. automodule:: aristotle_mdr.views.views
   :members: download
