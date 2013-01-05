from __future__ import print_function
from inspect import isclass, getmembers
from importlib import import_module
from itertools import imap, repeat

from sqlalchemy.exc import IntegrityError, OperationalError
from savalidation import ValidationError
from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.restless import APIManager

API_EXCEPTIONS = [ValidationError, ValueError, AttributeError, TypeError,
	IntegrityError, OperationalError]

db = SQLAlchemy()
module_names = ['hermes']
model_names = ['app.%s.models' % x for x in module_names]
bp_names = ['app.%s.views' % x for x in module_names]
model_alias = 'model'


def _get_app_classes(module):
	classes = getmembers(module, isclass)
	app_classes = filter(lambda x: str(x[1]).startswith("<class 'app"), classes)
	return ['%s' % x[0] for x in app_classes]


def create_app(config_mode=None, config_file=None):
	# Create webapp instance
	app = Flask(__name__)
	db.init_app(app)
	Bootstrap(app)
	app.config.from_envvar('APP_SETTINGS', silent=True)

	if config_mode:
		app.config.from_object('config.%s' % config_mode)
	if config_file:
		app.config.from_pyfile(config_file)

	[app.register_blueprint(bp) for bp in blueprints]

	# set g variables
	@app.before_request
	def before_request():
		g.site = app.config['SITE']
		g.topnav = app.config['TOPNAV']
		g.hero = app.config['HERO']
		g.sub_units = app.config['SUB_UNITS']

	@app.errorhandler(404)
	@app.errorhandler(TypeError)
	def not_found(error):
		heading = 'Page not found.'
		text = "Sorry, your page isn't available!."
		kwargs = {'id': 404, 'title': '404', 'heading': heading, 'text': text}
		return render_template('page.html', **kwargs), 404

	@app.template_filter()
	def currency(x):
		try:
			return '$%.2f' % x
		except TypeError:
			return x

	@app.route('/')
	def home():
		return render_template('home.html')

	# app.jinja_env.filters['currency']=currency

	# Create the Flask-Restless API manager.
	mgr = APIManager(app, flask_sqlalchemy_db=db)

	kwargs = {'methods': app.config['API_METHODS'],
		'validation_exceptions': API_EXCEPTIONS,
		'allow_functions': app.config['API_ALLOW_FUNCTIONS'],
		'allow_patch_many': app.config['API_ALLOW_PATCH_MANY']}

	# provides a nested list of class names grouped by model in the form [[],[]]
	# [[], ['Event', 'Type']]
	nested_classes = map(_get_app_classes, models)

	# provides a list of tuples (module, [list of class names])
	# in the form [(<module>,[]),(<module>,[])]
	# [(<module 'app.hermes.models' from '/path/to/models.pyc'>,
	# 	['Event', 'Type'])]
	sets = zip(models, nested_classes)

	# provides a nested iterator of classes in the expanded form of <class>
	# <class 'app.hermes.models.Event'>
	nested_tables = [imap(getattr, repeat(x[0]), x[1]) for x in sets]

	# Create API endpoints (available at /api/<tablename>)
	[[mgr.create_api(x, **kwargs) for x in tables] for tables in nested_tables]
	return app

# import app models
models = [import_module(x) for x in model_names]
views = [import_module(x) for x in bp_names]
blueprints = map(getattr, views, module_names)
