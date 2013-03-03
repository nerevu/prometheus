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


@manager.command
def popprices():
	"""Add price quotes from yahoo
	"""
	from pandas.io.data import DataReader

	with app.app_context():
		site = portify(url_for('api', _external=True))
		conn = Connection(site)
		table, filter = conn.securities
		objects = conn.get(table, filter)
		symbols = []
		[[symbols.append(c['symbol']) for c in o['commodities']] for o in objects]

		table, filter = conn.commodities(symbols)
		objects = conn.get(table, filter)
		starts = [max(c['date'] for c in o['commodity_prices']) for o in objects]
		set = zip(symbols, starts)

		for s in set:
			print s
# 			if s[1] < today():
# 				data = DataReader(s[0], "yahoo", s[1])
# 				raw = data.Close.to_dict().items()
# 				values = [[(get_id(s[0]), 1, r[1], r[0]) for r in raw]]
# 				tables = [s[0]]
# 				keys = [('commodity_id', 'currency_id', 'close', 'date')]
# 				content = conn.process(values, tables, keys)
# 				conn.post(content)
#
# 		print 'Prices table populated'

if __name__ == '__main__':
	manager.run()
