#!/usr/bin/env python
from app.hermes.models import init_db, pop_db
from os.path import abspath
from flask import current_app as app
from app import create_app, db
from flask.ext.script import Manager

manager = Manager(create_app)
manager.add_option('-m', '--cfgmode', dest='config_mode',
	default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=abspath)


def get_site():
	with app.app_context():
		domain = app.config['DOMAIN']
		return 'http://%s/api' % domain


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
		init_db(get_site())
		print 'Database initialized'


@manager.command
def popdb():
	with app.app_context():

		"""Removes all content from database and populates it
		with sample data
		"""
		initdb()
		pop_db(site)
		print 'Database populated'

if __name__ == '__main__':
	manager.run()
