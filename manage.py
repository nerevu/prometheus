#!/usr/bin/env python
import os.path as p

from subprocess import call
from pprint import pprint

from flask import current_app as app, url_for
from flask.ext.script import Manager
from app import create_app, db
from app.connection import Connection
from app.helper import get_init_values, get_pop_values, portify

manager = Manager(create_app)
manager.add_option(
	'-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=p.abspath)


@manager.command
def checkstage():
	"""Checks staged with git pre-commit hook"""

	path = p.join(p.dirname(__file__), 'app', 'tests', 'test.sh')
	cmd = "sh %s" % path
	return call(cmd, shell=True)


@manager.command
def runtests():
	"""Checks staged with git pre-commit hook"""

	cmd = 'nosetests -xv'
	return call(cmd, shell=True)


@manager.command
def createdb():
	"""Creates database if it doesn't already exist"""

	with app.app_context():
		db.create_all()
		print 'Database created'


@manager.command
def cleardb():
	"""Removes all content from database"""

	with app.app_context():
		db.drop_all()
		print 'Database cleared'


@manager.command
def resetdb():
	"""Removes all content from database and creates new tables"""

	with app.app_context():
		cleardb()
		createdb()


@manager.command
def testapi():
	"""Removes all content from database and to test the API"""

	with app.app_context():
		resetdb()
		site = portify(url_for('api', _external=True))
		conn = Connection(site)

		values = [[[('Yahoo')], [('Google')], [('XE')]]]
		tables = ['data_source']
		keys = [[('name')]]
		content = conn.process(values, tables, keys)
		print 'Attempting to post %s to %s at %s' % (
			content[0]['data'], tables[0], site)

		conn.post(content)
		print 'Content posted via API!'


@manager.command
def initdb():
	"""Removes all content from database and initializes it
		with default values
	"""

	with app.app_context():
		resetdb()
		site = portify(url_for('api', _external=True))
		conn = Connection(site)

		values = get_init_values()
		content = conn.process(values)
		conn.post(content)
		print 'Database initialized'


@manager.command
def popdb():
	"""Removes all content from database and populates it
		with sample data
	"""

	with app.app_context():
		initdb()
		site = portify(url_for('api', _external=True))
		conn = Connection(site)

		values = get_pop_values()
		content = conn.process(values)
		conn.post(content)
		print 'Database populated'


@manager.command
def clearprices():
	"""Clear prices table from database
	"""
	pass


@manager.option('-s', '--start', help='Start date')
@manager.option('-e', '--end', help='End date')
def popprices(start=None, end=None):
	"""Add price quotes
	"""
	import itertools as it
	from datetime import datetime as dt, date as d, timedelta
	from dateutil.parser import parse
	from app.hermes import Historical

	with app.app_context():
		site = portify(url_for('api', _external=True))
		portf = Historical(site)
		last_dates = portf.latest_price_date()
		end_date = parse(end).date() if end else d.today()

		if start:
			start_dates = it.repeat(parse(start).date(), len(portf.symbols))
		else:
			start_dates = [
				dt.strptime(ts, "%Y-%m-%dT%H:%M:%S").date() + timedelta(days=1)
				for ts in last_dates]

		set = zip(portf.symbols, start_dates)
		tables = ['price']
		keys = [('commodity_id', 'currency_id', 'close', 'date')]

		for s in set:
			if s[1] < end_date:
				values = [portf.get_prices(s[0], s[1], end_date)]

				if values:
					conn = Connection(site)
					content = conn.process(values, tables, keys)
# 					print content
					conn.post(content)
				else:
					print(
						'No prices found for %s from %s to %s' %
						(s[0], s[1], end_date))

		print 'Prices table populated'

if __name__ == '__main__':
	manager.run()
