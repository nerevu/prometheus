from os.path import abspath

from flask import current_app as app
from app import create_app, db
# from app.model import init_db
from flask.ext.script import Manager

manager = Manager(create_app)
manager.add_option('-m', '--cfgmode', dest='config_mode', default='Development')
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

		"""Clears database"""
		db.drop_all()
		print 'Database cleared'

@manager.command
def resetdb():
	with app.app_context():

		"""Resets database"""
		db.drop_all()
		db.create_all()
		print 'Database reset'

@manager.command
def initdb():
	with app.app_context():

		"""Initializes database with test data"""
		if prompt_bool('Are you sure you want to replace all data?'):
			init_db()
			print 'Database initialized'
		else:
			print 'Database initialization aborted'

if __name__ == '__main__':
	manager.run()
