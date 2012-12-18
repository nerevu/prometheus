from app import app, db
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager, Server

manager = Manager(app)
manager.add_command('runserver', Server())

@manager.command
def createdb():
	"""Creates database"""
	db.create_all()
	print 'Database created'

@manager.command
def cleardb():
	"""Clears database"""
	db.drop_all()
	print 'Database dropped'

@manager.command
def initdb():
	"""Initializes database with test data"""
	if prompt_bool('Are you sure you want to replace all data?'):
		try:
			from app import testing
		except ImportError:
			print "Unable to load 'testing' module"
			return 1

		testing.populate_test_db()
		print 'Database initialized'
	else:
		print 'Database initializatio aborted'

if __name__ == '__main__':
	Bootstrap(app)
	manager.run()
