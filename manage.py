from os.path import abspath
from flask import current_app as app
import tests
from app import create_app, db
# from app.model import init_db, populate_db
from flask.ext.script import Manager

manager = Manager(create_app)
manager.add_option('-m', '--cfgmode', dest='config_mode',
	default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=abspath)


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

		"""Initializes database with default values"""
		db.drop_all()
		db.create_all()
		init_db()
		print 'Database initialized'


@manager.command
def popdb():
	with app.app_context():

		"""Populates database with sample data"""
		db.drop_all()
		db.create_all()
		init_db()
		populate_db()
		print 'Database populated'

if __name__ == '__main__':
	manager.run()
