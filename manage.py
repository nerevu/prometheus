from app.hermes.models import init_db, pop_db
from os.path import abspath
from flask import current_app as app
from app import create_app, db
from flask.ext.script import Manager

manager = Manager(create_app)
manager.add_option('-m', '--cfgmode', dest='config_mode',
	default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=abspath)

site = 'http://127.0.0.1:5000/api'


@manager.command
def createdb():
	with app.app_context():

		"""Creates database"""
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
		db.drop_all()
		db.create_all()
		print 'Database reset'


@manager.command
def initdb():
	with app.app_context():

		"""Removes all content from database and Initializes database
		with default values
		"""
		resetdb()
		init_db(site)
		print 'Database initialized'


@manager.command
def popdb():
	with app.app_context():

		"""Removes all content from database and Populates database
		with sample data
		"""
		initdb()
		pop_db(site)
		print 'Database populated'

if __name__ == '__main__':
	manager.run()
