# -*- coding: utf-8 -*-
"""
	app
	~~~~~~~~~~~~~~

	Provides the flask application
"""

from __future__ import print_function

import re
import config

from inspect import isclass, getmembers
from functools import partial, update_wrapper
from importlib import import_module
from itertools import imap, repeat
from os import path as p, listdir
from sqlalchemy.exc import IntegrityError, OperationalError
from savalidation import ValidationError
from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.restless import APIManager
from flask.ext.markdown import Markdown

API_EXCEPTIONS = [
	ValidationError, ValueError, AttributeError, TypeError, IntegrityError,
	OperationalError]

db = SQLAlchemy()
__DIR__ = p.dirname(__file__)


def _get_modules(dir):
	dirs = listdir(dir)
	modules = [
		d for d in dirs if p.isfile(p.join(dir, d, '__init__.py'))
		and d != 'tests']

	return modules


def _get_app_classes(module):
	classes = getmembers(module, isclass)
	app_classes = filter(lambda x: str(x[1]).startswith("<class 'app"), classes)
	return ['%s' % x[0] for x in app_classes]


def _get_view_func(page, mkd_folder):
	path = p.join(__DIR__, mkd_folder, page['file'])
	text = open(path).read()
	pattern = '---'
	matches = [match for match in re.finditer(pattern, text)]

	if matches:
		cfg_start = matches[0].end() + 1
		cfg_end = matches[1].start() - 1
		parse = text[cfg_start:cfg_end].split('\n')
		cfg = dict([tuple(row.split(': ')) for row in parse])
		md = text[matches[1].end() + 1:]
	else:
		cfg = {}
		md = text

	kwargs = {'md': md, 'id': page['id'], 'cfg': cfg}
	endpoint = page['id']
	func = page['id']
	exec '%s = partial(_template, kwargs)' % func in globals(), locals()
	update_wrapper(eval(func), _template)
	eval(func).__name__ = func
	return eval(func)


def _template(kwargs):
	return render_template('markdown.html', **kwargs)


def create_app(config_mode=None, config_file=None):
	# Create webapp instance
	app = Flask(__name__)
	db.init_app(app)
	Bootstrap(app)
	Markdown(app)

	if config_mode:
		app.config.from_object(getattr(config, config_mode))
	elif config_file:
		app.config.from_pyfile(config_file)
	else:
		app.config.from_envvar('APP_SETTINGS', silent=True)

	[app.register_blueprint(bp) for bp in blueprints]

	# set g variables
	@app.before_request
	def before_request():
		g.site = app.config['SITE']
		g.topnav = app.config['TOPNAV']
		g.hero = app.config['HERO']
		g.sub_units = app.config['SUB_UNITS']

	@app.errorhandler(404)
# 	@app.errorhandler(TypeError)
	def not_found(error):
		heading = 'Page not found.'
		subheading = "Sorry, your page isn't available!"
		kwargs = {
			'id': 404, 'title': '404', 'heading': heading,
			'subheading': subheading}

		return render_template('page.html', **kwargs), 404

	@app.context_processor
	def utility_processor():
		def currency(x):
			try:
				return '$%.2f' % x
			except TypeError:
				return x
		return dict(currency=currency)

# 	@app.template_filter()
# 	def currency(x):
# 		try:
# 			return '$%.2f' % x
# 		except TypeError:
# 			return x

# 	app.jinja_env.filters['currency'] = currency

	@app.route('/')
	def home():
		return render_template('home.html')

	# create markdown views
	mkd_pages = app.config['MKD_PAGES']
	mkd_folder = app.config['MKD_FOLDER']

	for page in mkd_pages:
		func = _get_view_func(page, mkd_folder)
		app.add_url_rule('/%s/' % endpoint, view_func=func)

	# Create the Flask-Restless API manager.
	mgr = APIManager(app, flask_sqlalchemy_db=db)

	kwargs = {
		'methods': app.config['API_METHODS'],
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

# dynamically import app models and views
modules = _get_modules(__DIR__)
model_names = ['app.%s.models' % x for x in modules]
view_names = ['app.%s.views' % x for x in modules]
models = [import_module(x) for x in model_names]
views = [import_module(x) for x in view_names]
blueprints = map(getattr, views, modules)
