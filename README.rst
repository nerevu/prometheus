prometheus |build|
==================

.. |build| image:: https://secure.travis-ci.org/reubano/prometheus.png

.. image:: https://raw.github.com/reubano/prometheus/master/screenshot.png
   :width: 500pt

Introduction
------------

Prometheus is a `Flask <http://flask.pocoo.org>`_ (`About Flask`_) powered web app that tells you how your stock portfolio has performed over time, gives insight into how to optimize your asset allocation, and monitors your portfolio for rebalancing or performance enhancing opportunities. It has been tested on the following configuration:

- MacOS X 10.7.5
- Python 2.7.4

Requirements
------------

Prometheus requires the following in order to run properly:

- `Python >= 2.7 <http://www.python.org/download>`_

Features
--------

Prometheus aims to give investors an easy way to:

- construct portfolios of low cost ETFs and mutual funds
- generate customized portfolios based on their individual risk tolerance
- access asset classes that have since only been available to the elite

Prometheus provides a suite of tools to:

- track and monitor portfolio performance and allocation
- compare portfolios across various categories (account, manager, etc.)
- visualize various portfolio metrics

Framework
---------

Flask Extensions
^^^^^^^^^^^^^^^^

- Database abstraction with `SQLAlchemy <http://www.sqlalchemy.org>`_.
- Web forms validation with `WTForms <http://wtforms.simplecodes.com/>`_.
- Script support with `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_.
- `Bootstrap <https://github.com/twitter/bootstrap>`_ integration with `Flask-Bootstrap <http://pypi.python.org/pypi/Flask-Bootstrap>`_
- Markdown parsing with `Flask-Markdown <https://readthedocs.org/projects/flask-markdown/>`_
- Database validation with `SAValidation <https://pypi.python.org/pypi/SAValidation>`_
- RESTful API generation with `Flask-Restless <http://flask-restless.readthedocs.org/>`_

Production Server
^^^^^^^^^^^^^^^^^

- `gunicorn <http://gunicorn.org/>`_
- `gevent <http://www.gevent.org/>`_


Quick Start
-----------

*Clone the repo*

::

	git clone git@github.com:reubano/prometheus.git
	cd prometheus

*Install requirements*

::

	sudo easy_install pip
	sudo pip install -r requirements-local.txt

*Run server*

	./manage.py runserver

Now *view the app* at ``http://localhost:5000``

Scripts
-------

Prometheus comes with a built in script manager ``manage.py``. Use it to start the
server, run tests, and initialize the database.

Usage
^^^^^

	./manage.py <command> [command-options] [manager-options]

Examples
^^^^^^^^

*Start server*

	./manage.py runserver

*Run nose tests*

	./manage.py runtests

*Initialize the production database*

	./manage.py initdb -m Production

Manager options
^^^^^^^^^^^^^^^

::

	  -m MODE, --cfgmode=MODE  set the configuration mode, must be one of
	                           ['Production', 'Development', 'Test'] defaults
	                           to 'Development'. See `config.py` for details
	  -f FILE, --cfgfile=FILE  set the configuration file (absolute path)

Commands
^^^^^^^^

::

	  checkstage  Checks staged with git pre-commit hook
	  initdb      Removes all content from database and initializes it
	              with default values
	  popdb       Removes all content from database initializes it, and
	              populates it with sample data
	  popprices   Add prices for all securities in the database
	  runserver   Runs the Flask development server i.e. app.run()
	  runtests    Run nose tests
	  shell       Runs a Python shell inside Flask application context.
	  resetdb     Remove all content from database and creates new tables
	  testapi     Test to see if API is working

Command options
^^^^^^^^^^^^^^^

Type ``./manage.py <command> -h`` to view any command's options

	./manage.py manage runserver -h

::

	usage: ./manage.py runserver [-h] [-t HOST] [-p PORT] [--threaded]
	                             [--processes PROCESSES] [--passthrough-errors]
	                             [-d] [-r]

	Runs the Flask development server i.e. app.run()

	optional arguments:
	  -h, --help              show this help message and exit
	  -t HOST, --host HOST
	  -p PORT, --port PORT
	  --threaded
	  --processes PROCESSES
	  --passthrough-errors
	  -d, --no-debug
	  -r, --no-reload

Example
^^^^^^^

*Start production server on port 1000*

	./manage.py runserver -p 1000 -m Production

Configuration
-------------

Config Variables
^^^^^^^^^^^^^^^^

The following configurations settings are in ``config.py``:

======================== =================== ===================
variable                 description         default value
======================== =================== ===================
__APP_NAME__             application name    'Prometheus'
__YOUR_NAME__            your name           'Reuben Cummings'
__YOUR_EMAIL__           your email address  <user>@gmail.com
__YOUR_WEBSITE__         your website        'http://<user>.github.com'
__API_BASE__             api base url        'http://prometheus-api.herokuapp.com/'
======================== =================== ===================

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

Prometheus will reference the following environment variables in ``config.py``
if they are set on your system.

::

	SECRET_KEY
	CSRF_SESSION_KEY
	RECAPTCHA_PUBLIC_KEY
	RECAPTCHA_PRIVATE_KEY
	GOOGLE_ANALYTICS_ACCOUNT

To set an environment variable, *do the following*:

	echo 'export VARIABLE=value' >> ~/.profile

Advanced Installation
---------------------

Virtual environment setup
^^^^^^^^^^^^^^^^^^^^^^^^^

Ideally, you should install modules for every project into a `virtual environment <http://blog.sidmitra.com/manage-multiple-projects-better-with-virtuale>`_.
This setup will allow you to install different versions of the same module into different
projects without worrying about adverse interactions.

	sudo pip install virtualenv virtualenvwrapper

*Add the following* to your ``~/.profile``

::

	export WORKON_HOME=$HOME/.virtualenvs
	export PIP_VIRTUALENV_BASE=$WORKON_HOME
	export PIP_RESPECT_VIRTUALENV=true
	source /usr/local/bin/virtualenvwrapper.sh

*Create your new virtualenv*

::

	mkvirtualenv --no-site-packages prometheus
	sudo easy_install pip
	sudo pip install -r requirements-local.txt

*Patch pandas to enable dividend and split fetching*

	patch -p0 < data.py.patch

API setup
^^^^^^^^^^^^^^^^^

By default, this project uses the `Heroku hosted <http://prometheus-api.herokuapp.com>`_ `Prometheus-API <https://github.com/reubano/prometheus-api>`_.
If you would like to host your own API do the following:

*Clone the repo*

::

	git clone git@github.com:reubano/prometheus-api.git
	cd prometheus-api

*Install requirements*

::

	mkvirtualenv --no-site-packages prometheus-api
	workon prometheus-api
	sudo pip install -r requirements-local.txt

*Run server* (pick a different port than the main app)

	./manage.py runserver -p 5005

Now that your api is up and running at http://localhost:5005, set the
``__API_BASE__`` variable in ``config.py`` to the url of your new api.

Production Server
^^^^^^^^^^^^^^^^^

Getting Gevent up and running is a bit tricky so follow these instructions carefully.

To use ``gevent``, you first need to install ``libevent``.

*Linux*

	apt-get install libevent-dev

*Mac OS X via* `homebrew <http://mxcl.github.com/homebrew/>`_

	brew install libevent

*Mac OS X via* `macports <http://www.macports.com/>`_

	sudo port install libevent

*Mac OS X via DMG*

	`download on Rudix <http://rudix.org/packages-jkl.html#libevent>`_

Now that libevent is handy, *install the remaining requirements*

	sudo pip install -r requirements.txt

Or via the following if you installed libevent from macports

::

	sudo CFLAGS="-I /opt/local/include -L /opt/local/lib" pip install gevent
	sudo pip install -r requirements.txt

Finally, *install foreman*

	sudo gem install foreman

Now, you can *run the application locally*

	foreman start

You can also *specify what port you'd prefer to use*

	foreman start -p 5555

Deployment
^^^^^^^^^^

If you haven't `signed up for Heroku <https://api.heroku.com/signup>`_, go
ahead and do that. You should then be able to `add your SSH key to
Heroku <http://devcenter.heroku.com/articles/quickstart>`_, and also
`heroku login` from the commandline.

*Install heroku and create your app*

::

	sudo gem install heroku
	heroku create -s cedar app_name

Now before pushing to Heroku, *temporarily remove ``pandas`` from the
requirements file* (there is a bug where heroku won't install ``pandas`` unless
``numpy`` is already installed)

::

	pip freeze -l | sed '/pandas/d' > requirements.txt
	git commit -am "Remove pandas as requirement"
	git push heroku master

*Replace ``pandas`` and push to Heroku*

	pip freeze -l > requirements.txt
	git commit -am "Add pandas as requirement"
	git push heroku master

*Start the web instance and make sure the application is up and running*

::

	heroku ps:scale web=1
	heroku ps

Now, we can *view the application in our web browser*

	heroku open

And anytime you want to redeploy, it's as simple as ``git push heroku master``.
Once you are done coding, deactivate your virtualenv with ``deactivate``.

Directory Structure
-------------------

	tree . | sed 's/+----/├──/' | sed '/.pyc/d' | sed '/.DS_Store/d'

::

    prometheus
         ├──Procfile                        (heroku process)
         ├──README.rst                      (this file)
         ├──app
         |   ├──__init__.py                 (main app module)
         |   ├──apollo                      (visualization engine)
         |   |    ├──__init__.py            (main apollo module)
         |   |    ├──views.py
         |   ├──connection.py               (api interface module)
         |   ├──cronus                      (portfolio analytics engine)
         |   |    ├──__init__.py            (blank - see sub modules)
         |   |    ├──analytics.py
         |   |    ├──coredata.py
         |   |    ├──forms.py
         |   |    ├──sources.py
         |   |    ├──views.py
         |   ├──favicon.ico
         |   ├──helper.py                   (manage/views/forms helper)
         |   ├──hermes                      (price/event data aggregator)
         |   |    ├──__init__.py            (main hermes module)
         |   |    ├──forms.py
         |   |    ├──views.py
         |   ├──LICENSE
         |   ├──MANIFEST.in                 (pypi includes)
         |   ├──markdown                    (static pages - auto parsed into html)
         |   |    ├──about.md
         |   |    ├──api.md
         |   ├──README.rst                  (symlink for pypi)
         |   ├──setup.py                    (pypi settings)
         |   ├──templates                   (Jinja templates)
         |   |    ├──barchart.html
         |   |    ├──base.html
         |   |    ├──entry.html
         |   |    ├──footer.html
         |   |    ├──home.html
         |   |    ├──markdown.html
         |   |    ├──page.html
         |   |    ├──topnav.html
         |   ├──tests
         |        ├──__init__.py            (main tests module)
         |        ├──standard.rc            (pylint config)
         |        ├──test.sh                (git pre-commit hook)
         |        ├──test_cronus.py
         |        ├──test_hermes.py
         |        ├──test_site.py
         |        ├──trnx.csv
         ├──config.py                       (app config)
         ├──manage.py                       (flask-script)
         ├──requirements.txt                (python module requirements)
         ├──runtime.txt                     (python version)
         ├──setup.cfg                       (unit test settings)

Contributing
------------

*First time*

1. Fork
2. Clone
3. Code (if you are having problems committing because of git pre-commit
   hook errors, just run ``./manage.py checkstage`` to see what the issues are.)
4. Use tabs **not** spaces
5. Add upstream ``git remote add upstream https://github.com/reubano/prometheus.git``
6. Rebase ``git rebase upstream/master``
7. Test ``./manage.py runtests``
8. Push ``git push origin master``
9. Submit a pull request

*Continuing*

1. Code (if you are having problems committing because of git pre-commit
   hook errors, just run ``./manage.py checkstage`` to see what the issues are.)
2. Use tabs **not** spaces
3. Update upstream ``git fetch upstream``
4. Rebase ``git rebase upstream/master``
5. Test ``./manage.py runtests``
6. Push ``git push origin master``
7. Submit a pull request

Contributors
------------

	git shortlog -sn

::

	commits: 405
	  404  Reuben Cummings
 	    1  Luke Cyca

Inspiration
-----------

Prometheus is modeled after Dirk Eddelbuettel's `beancounter <http://eddelbuettel.com/dirk/code/beancounter.html>`_ and `smtm <http://dirk.eddelbuettel.com/code/smtm.html>`_.

About Flask
-----------

`Flask <http://flask.pocoo.org>`_ is a BSD-licensed microframework for Python based on
`Werkzeug <http://werkzeug.pocoo.org/>`_, `Jinja2 <http://jinja.pocoo.org>`_ and good intentions.

License
-------

Prometheus is distributed under the `BSD License <http://opensource.org/licenses/bsd-3-license.php>`_, the same as `Flask <http://flask.pocoo.org>`_ on which this program depends.
