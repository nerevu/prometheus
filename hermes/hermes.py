import savalidation.validators as val

from os import path
from datetime import datetime as dt
from datetime import date as d
from flask import Flask, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from sqlalchemy.exc import IntegrityError, OperationalError
# from sqlalchemy.schema import UniqueConstraint
from savalidation import ValidationMixin, ValidationError
from formencode.validators import Invalid

app = Flask(__name__)
app.config['DEBUG'] = True
db_uri = 'sqlite:///%s' % path.join(path.expanduser('~'), 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class Type(db.Model, ValidationMixin):
	# schema
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	name = db.Column(db.String(50), nullable=False, unique=True)
	unit = db.Column(db.String(25), nullable=False, default='USD')

	# validation
	val.validates_constraints()

# 	def __init__(self, name, unit='USD', utc_created=None, utc_updated=None):
# 		self.name = name
# 		self.unit = unit
# 		self.utc_created = (utc_created or dt.utcnow())
# 		self.utc_updated = (utc_updated or dt.utcnow())
#
# 	def __repr__(self):
# 		return 'Type<name=%s, unit=%s>' % (self.name, self.unit)

class Event(db.Model, ValidationMixin):
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	symbol = db.Column(db.String(10), nullable=False)
	date = db.Column(db.Date, nullable=False, default=d.today())
	type_id = db.Column(db.Integer, db.ForeignKey('type.id'),
		nullable=False)
	type = db.relationship('Type',
		backref=db.backref('events', lazy='joined'), lazy='joined')
	# lazy='dynamic' gives errors
	value = db.Column(db.Float, nullable=False)

	# validation
	# UniqueConstraint('symbol', 'date', 'type_id', 'value')
	val.validates_constraints()

# 	def __init__(self, symbol, value='USD', date=None, utc_created=None, utc_updated=None):
# 		self.symbol = symbol
# 		self.value = value
# 		self.date = (date or d.today())
# 		self.utc_created = (utc_created or dt.utcnow())
# 		self.utc_updated = (utc_updated or dt.utcnow())
#
# 	def __repr__(self):
# 		return ('Event<symbol=%s, value=%s, date=%s>'
# 			% (self.symbol, self.value, self.date))

# Create the database tables.
db.create_all()

# Create the Flask-Restless API manager.
manager = APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
type_blueprint = manager.create_api(
	Type, methods=['GET', 'POST', 'DELETE'], allow_functions='true',
	validation_exceptions=[ValidationError, ValueError, AttributeError,
		TypeError, IntegrityError, OperationalError])

event_blueprint = manager.create_api(
	Event, methods=['GET', 'POST', 'DELETE'], allow_functions='true',
	validation_exceptions=[ValidationError, ValueError, AttributeError,
		TypeError, IntegrityError, OperationalError])

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/event/<int:event_id>')
def show_event(event_id):
	# show the post with the given id, the id is an integer
	return 'Event %d' % event_id

@app.errorhandler(404)
def page_not_found(error):
	return render_template('page_not_found.html'), 404


if __name__ == '__main__':
	app.run()
