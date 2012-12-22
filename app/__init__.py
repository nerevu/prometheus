from __future__ import print_function
from inspect import isclass, getmembers
from importlib import import_module
from itertools import imap, starmap, repeat
from datetime import date as d

from sqlalchemy.exc import IntegrityError, OperationalError
from savalidation import ValidationError
from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.restless import APIManager

API_EXCEPTIONS = [ValidationError, ValueError, AttributeError, TypeError,
	IntegrityError, OperationalError]

db = SQLAlchemy()
module_names = ['main', 'hermes']
model_names = ['app.%s.models' % x for x in module_names]
bp_names = ['app.%s.views' % x for x in module_names]
model_alias = 'model'

topnav = [{'id': 'events', 'caption': 'Events', 'location': 'hermes.get',
	'table': 'event'}, {'id': 'types', 'caption': 'Types',
	'location': 'hermes.get', 'table': 'event_type'}, {'id': 'prices',
	'caption': 'Prices', 'location': 'hermes.get', 'table': 'price'},
	{'id': 'commodities', 'caption': 'Commodities', 'location': 'hermes.get',
	'table': 'commodity'}, {'id': 'worth', 'caption': 'Net Worth',
	'location': 'hermes.worth'}, {'id': 'api', 'caption': 'API',
	'location': 'hermes.api'}]

hero = {'heading': 'Prometheus: a global asset allocation tool',
	'text': 'Prometheus is a full featured web app that tells you how your '
	'stock portfolio has performed over time and gives insight into how to '
	'optimize your asset allocation. Additionally, Prometheus monitors your '
	'portfolio to alert you when you need to rebalance or if you are '
	'consistently underpeforming the market on a risk adjusted basis.',
	'location': 'main.about'}

sub_units = [{'heading': 'Events', 'text': 'See all your stocks events in one '
	'convenient location. Track stock splits, dividend payments, mergers '
	'and more!', 'location': 'hermes.get', 'table': 'event'},
	{'heading': 'Prices', 'text': 'Update your stock prices with the click '
	'of a button! Automatically grap the latest pricing information from '
	'Yahoo or Google.', 'location': 'hermes.get', 'table': 'price'},
	{'heading': 'Net Worth', 'text': 'See how the value of your portfolio '
	'over time with these sleek interactive charts! Instantly see how the '
	'effects of dividends impacts your return.', 'location': 'hermes.worth'}]

site = {'id': 'prometheus', 'caption': 'Prometheus',
	'date': d.today().strftime("%Y"), 'author': 'Reuben Cummings',
	'author_url': 'http://reubano.github.com', 'sub_span': 12 / len(sub_units),
	'location': 'main.home'}


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
		g.site = site
		g.topnav = topnav
		g.hero = hero
		g.sub_units = sub_units

	@app.errorhandler(404)
	def not_found(error):
		return render_template('404.html'), 404

	@app.template_filter()
	def currency(x):
		try:
			return '$%.2f' % x
		except TypeError:
			return x

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
	sets = map(lambda x, y: (x, y), models, nested_classes)

	# provides a nested iterator of classes in the expanded form of <class>
	# <class 'app.hermes.models.Event'>
	nested_tables = [imap(getattr, repeat(x[0]), x[1]) for x in sets]

	# Create API endpoints (available at /api/<tablename>)
	[[mgr.create_api(x, **kwargs) for x in tables] for tables in nested_tables]
	return app

# import app.hermes.models
models = [import_module(x) for x in model_names]
views = [import_module(x) for x in bp_names]
blueprints = map(getattr, views, module_names)
