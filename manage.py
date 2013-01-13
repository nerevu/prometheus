#!/usr/bin/env python
from pprint import pprint
from os.path import abspath

from flask import current_app as app, url_for
from flask.ext.script import Manager
from app import create_app, db
from app.manage_helper import init_db, pop_db

manager = Manager(create_app)
manager.add_option(
	'-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=abspath)


def get_api_endpoint():
	with app.app_context():
		site = url_for('api', _external=True).split('/')

		if site[2] == 'localhost':
			site[2] = 'localhost:%s' % app.config['PORT']

		site = '/'.join(site)
		return site


@manager.command
def createdb():
	with app.app_context():

		"""Creates database if it doesn't already exist"""
		db.create_all()
		print 'Database created'


@manager.command
def cleardb():
	with app.app_context():

		"""Removes all content from database"""
		db.drop_all()
		print 'Database cleared'


@manager.command
def resetdb():
	with app.app_context():

		"""Removes all content from database and creates new tables"""
		cleardb()
		createdb()


@manager.command
def initdb():
	with app.app_context():

		"""Removes all content from database and initializes it
		with default values
		"""
		resetdb()
		r = init_db(get_api_endpoint())
		print 'Database initialized'


@manager.command
def popdb():
	with app.app_context():

		"""Removes all content from database and populates it
		with sample data
		"""
		initdb()
		r = pop_db(get_api_endpoint())
		print 'Database populated'

if __name__ == '__main__':
	manager.run()
