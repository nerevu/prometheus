#!/usr/bin/env python
import os.path as p
import itertools as it

from subprocess import call
from pprint import pprint
from datetime import datetime as dt, date as d, timedelta

from flask import current_app as app
from flask.ext.script import Manager
from app import create_app
from app.connection import Connection
from app.hermes import Historical
from app.helper import app_site

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
	"""Run nose tests"""
	cmd = 'nosetests -xv'
	return call(cmd, shell=True)


@manager.command
def resetdb():
	"""Remove all content from database and creates new tables"""
	conn = Connection(app_site())
	conn.get('reset')
	print 'Database reset'


@manager.command
def testapi():
	"""Test to see if API is working"""
	conn = Connection(app_site())

	print 'Attempting to get data from API...'
	conn.get('data_source')
	print 'Content retreived via API!'


def post_all(conn, keys):
	"""Add prices, dividends, and splits for all securities in the database
	"""
	iter = []
	symbols = list(it.chain(conn.currencies, conn.securities))
	prices = conn.get_price_list(symbols)
	dividends = conn.get_price_list(conn.securities, extra='divs')
	splits = conn.get_price_list(conn.securities, extra='splits')
	iter.append(prices)
	iter.append(dividends)
	iter.append(splits)
	content = [conn.process(v, keys) for v in iter]
	[conn.post(values) for values in content]


@manager.command
def initdb():
	"""Remove all content from database and initializes it
		with default values
	"""
	resetdb()
	conn = Historical(app_site())
	date = d.today() - timedelta(days=45)
	keys = conn.get('keys')
	content = [conn.process(v, keys) for v in conn.get('init_values')]
	[conn.post(values) for values in content]
	post_all(conn, keys)

	price = conn.get_first_price(conn.securities, date)
	conn.post(conn.process(price, keys))
	print 'Database initialized'


@manager.command
def popdb():
	"""Remove all content from database, initializes it, and populates it
		with sample data
	"""
	initdb()
	conn = Historical(app_site())
	date = d.today() - timedelta(days=30)
	keys = conn.get('keys')
	content = [conn.process(v, keys) for v in conn.get('pop_values')]
	[conn.post(values) for values in content]
	post_all(conn, keys)

	price = conn.get_first_price(conn.securities, date)
	conn.post(conn.process(price, keys))
	print 'Database populated'


@manager.option(
	'-s', '--sym', help='Symbols (leave blank to update all securities)')
@manager.option('-a', '--start', help='Start date, defaults to last month')
@manager.option('-e', '--end', help='End date, defaults to today')
@manager.option(
	'-x', '--extra', help='Fetch [d]ividends or [s]plits in addition to prices')
def popprices(sym=None, start=None, end=None, extra=None):
	"""Add prices (and optionally dividends or splits) to securities
	in the database
	"""

	with app.app_context():
		conn = Historical(app_site())
		keys = conn.get('keys')
		sym = sym.split(',') if sym else None
		values = conn.get_price_list(sym, start, end, extra)

		conn.post(conn.process(values, keys))
		print 'Prices table populated'

if __name__ == '__main__':
	manager.run()
