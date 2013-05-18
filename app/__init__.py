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
from flask import Flask, render_template, g, flash, redirect, url_for

from flask.views import View
from flask.ext.bootstrap import Bootstrap
from flask.ext.markdown import Markdown

__DIR__ = p.dirname(__file__)


def _get_modules(dir):
	dirs = listdir(dir)
	modules = [
		d for d in dirs if p.isfile(p.join(dir, d, '__init__.py'))
		and d != 'tests']

	return modules


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
		app.add_url_rule('/%s/' % page['id'], view_func=func)

	return app


class Add(View):
	def dispatch_request(self, table=None):
		table = (table or self.table)
		form, conn, redir = self.get_vars(table)
		name = table.replace('_', ' ')

		if form.validate_on_submit():
			self.bookmark_table(table)
			key_list = list(set(form._fields.keys()).difference(['csrf_token']))
			values = {table: [tuple(getattr(form, k).data for k in key_list)]}
			keys = {table: key_list}
			content = conn.process(values, keys)
			conn.post(content)

			flash(
				'Awesome! You just posted a new %s.' % name,
				'alert alert-success')

		else:
			[flash('%s: %s.' % (k.title(), v[0]), 'alert alert-error')
				for k, v in form.errors.iteritems()]

		return redirect(url_for(redir, table=table))


# dynamically import app models and views
modules = _get_modules(__DIR__)
view_names = ['app.%s.views' % x for x in modules]
views = [import_module(x) for x in view_names]
blueprints = map(getattr, views, modules)
