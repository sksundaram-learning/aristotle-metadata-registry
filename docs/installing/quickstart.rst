Quick start documentation
------------------------

This is a quick and dirty guide to setting up a new metadata registry based on
the Aristotle MetaData Registry framework.

Such a server should be considered for *demonstration* purposes, and deployment
should be done in accordance with the best practices and specific requirements
of the installing agency.

For more information on configuring a more complete installation review the help article
:doc:`/installing/integrate_with_django_project`.

1. Make sure you have a server setup for hosting the project with an appropriate
   WSGI web server configured. If the server is only used for development, the inbuilt
   django server can be accessed by running the ``./manage.py runserver`` command.

   `PythonAnywhere also provides a free python server suitable for development and low
   traffic sites <http://www.PythonAnywhere.com>`_.

2. (Optional but recommended) Configure a ``virtualenv`` for your server, so that the dependancies
   for Aristotle-MDR do conflict any other software you may be running. If you are running
   Aristotle on an isolated server with root privileges you may skip this step.

   For PythonAnywhere, information is available on
   `installing virtualenv <https://www.pythonanywhere.com/wiki/InstallingVirtualenvWrapper>`_
   and `configuring a new virtualenv <https://www.pythonanywhere.com/wiki/VirtualEnvForNewerDjango>`_.

3. Fetch the example metadata registry stored within the
   `Aristotle-MDR GitHub repository <https://github.com/aristotle-mdr/aristotle-metadata-registry>`_.

   On a linux machine, this can be done with the command::

       svn export https://github.com/aristotle-mdr/aristotle-metadata-registry/trunk/example_mdr/

4. Browse to the ``example_mdr/example_mdr`` directory, and edit the ``settings.py`` files to meet your requirements.
   **It is strongly recommmended you generate a fresh **``SECRET_KEY``, also consider which
   database should be used and the customisation settings in the ``ARISTOTLE_SETTINGS``
   dictionary - details of which can be found under :doc:`/installing/settings`.

   The example registry includes commented out lines for some useful Aristotle-MDR extensions.
   If you wish to use these, removed the comments as directed by the documentation in ``settings.py``.

5. Install the requirements for aristotle using the Python PIP package manager::

    pip install -r requirements.txt

6. Migrate and setup the database for your new registry. if you have ``DEBUG`` set to ``True``
   this step will also create some example users and items::

    ./manage.py migrate

7. If you are using a WSGI server (such as PythonAnywhere) you'll need to either point your server to
   the `example_mdr/example_mdr/wsgi.py`` file or updated your WSGI configuration.

   For more information on `configuring the PythonAnywhere WSGI server review their documentation <https://www.pythonanywhere.com/wiki/DjangoTutorial>`_.

8. Start (or restart your server) the development server and visit its address.

