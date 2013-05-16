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


def post_all(conn):
	symbols = list(it.chain(conn.currencies, conn.securities))
	prices = conn.get_price_list(symbols)
	dividends = conn.get_price_list(conn.securities, extra='divs')
	splits = conn.get_price_list(conn.securities, extra='splits')

	values = list(it.chain(prices, dividends, splits))
	tables = ['price', 'event', 'event']

	conn.post(conn.process(values, tables))


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
def cleardb():
	"""Removes all content from database"""

	print 'Database cleared'


@manager.command
def testapi():
	"""Test to see if API is working"""
	site = app_site()
	conn = Connection(site)
	table = 'data_source'

	print 'Attempting to get data from %s' % table
	conn.get(table)
	print 'Content retreived via API!'


@manager.command
def initdb():
	"""Removes all content from database and initializes it
		with default values
	"""
	date = d.today() - timedelta(days=45)
	cleardb()
	conn = Historical(app_site())

	values = get_init_values()
	conn.post(conn.process(values))
	post_all(conn)

	price = conn.get_first_price(conn.securities, date)
	conn.post(conn.process(price, 'transaction'))
	print 'Database initialized'


@manager.command
def popdb():
	"""Removes all content from database initializes it, and populates it
		with sample data
	"""
	date = d.today() - timedelta(days=30)
	initdb()
	conn = Historical(app_site())

	values = get_pop_values()
	conn.post(conn.process(values, ['commodity', 'holding']))
	post_all(conn)

	price = conn.get_first_price(conn.securities, date)
	conn.post(conn.process(price, 'transaction'))
	print 'Database populated'


@manager.option('-s', '--sym', help='Symbols')
@manager.option('-t', '--start', help='Start date')
@manager.option('-e', '--end', help='End date')
@manager.option('-x', '--extra', help='Add [d]ividends or [s]plits')
def popprices(sym=None, start=None, end=None, extra=None):
	"""Add prices for all securities in the database
	"""

	with app.app_context():
		conn = Historical(app_site())
		sym = sym.split(',') if sym else None
		divs = True if (extra and extra.startswith('d')) else False
		splits = True if (extra and extra.startswith('s')) else False

		values = conn.get_price_list(sym, start, end, extra)
		table = 'event' if (divs or splits) else 'price'

		conn.post(conn.process(values, table))
		print 'Prices table populated'

if __name__ == '__main__':
	manager.run()
