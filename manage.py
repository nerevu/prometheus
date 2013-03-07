#!/usr/bin/env python
import os.path as p
import itertools as it

from subprocess import call
from pprint import pprint

from flask import current_app as app, url_for
from flask.ext.script import Manager
from app import create_app, db
from app.connection import Connection
from app.hermes import Historical
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
		tables = 'data_source'
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
		conn = Historical(site)

		values = get_init_values()
		conn.post(conn.process(values))

		symbols = list(it.chain(conn.currencies, conn.securities))
		prices = conn.get_prices(symbols)
		conn.post(conn.process(prices, conn.price_tables, conn.price_keys))
		print 'Database initialized'


@manager.command
def popdb():
	"""Removes all content from database and populates it
		with sample data
	"""

	with app.app_context():
		initdb()
		site = portify(url_for('api', _external=True))
		conn = Historical(site)

		values = get_pop_values()
		conn.post(conn.process(values))

		prices = conn.get_prices(['WMT', 'CAT', 'IBM'])
		conn.post(conn.process(prices, conn.price_tables, conn.price_keys))
		print 'Database populated'


@manager.option('-s', '--start', help='Start date')
@manager.option('-e', '--end', help='End date')
@manager.option('-S', '--sym', help='Symbols')
def popprices(start=None, end=None, sym=None):
	"""Add price quotes
	"""

	with app.app_context():
		site = portify(url_for('api', _external=True))
		conn = Historical(site)
		sym = sym.split(',') if sym else None
		prices = conn.get_prices(sym, start, end)

		conn.post(conn.process(prices, conn.price_tables, conn.price_keys))
		print 'Prices table populated'

if __name__ == '__main__':
	manager.run()
