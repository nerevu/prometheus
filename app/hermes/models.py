# from __future__ import print_function
import savalidation.validators as val

from inspect import isclass, getmembers
from sys import modules
from datetime import datetime as dt, date as d

from app import app, db
from sqlalchemy.exc import IntegrityError, OperationalError
from savalidation import ValidationMixin, ValidationError
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy.schema import UniqueConstraint

class Type(db.Model, ValidationMixin):
	# schema
	__tablename__ = 'hermes_type'
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	name = db.Column(db.String(50), nullable=False, unique=True)
	unit = db.Column(db.String(25), nullable=False, default='USD')

	# validation
	val.validates_constraints()

	def __init__(self, name=None, unit=None):
		self.name = name
		self.unit = unit

	def getUnit(self):
		return self.unit

	def __repr__(self):
		return '<Type(%r, %r)>' % (self.name, self.unit)

class Event(db.Model, ValidationMixin):
	__tablename__ = 'hermes_event'
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	symbol = db.Column(db.String(10), nullable=False)
	value = db.Column(db.Float, nullable=False)
	type_id = db.Column(db.Integer, db.ForeignKey('hermes_type.id'))
	type = db.relationship('Type', backref='events', lazy='joined')
	date = db.Column(db.Date, nullable=False, default=d.today())

	# validation
	# UniqueConstraint('symbol', 'date', 'type_id', 'value')
	val.validates_constraints()

	def __init__(self, symbol=None, value=None, type=None, type_id=None, date=None):
		self.symbol = symbol
		self.value = value
		self.type_id = type_id
		self.type = type
		self.date = (date or d.today())

	def __repr__(self):
		return ('<Type(%r, %r, %r, %r)>'
			% (self.symbol, self.value, self.type_id, self.date))

# Create the Flask-Restless API manager.
mgr = APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints (available at /api/<tablename>)
API_EXCEPTIONS = [ValidationError, ValueError, AttributeError, TypeError, IntegrityError, OperationalError]

kwargs = {
	'methods': app.config['API_METHODS'],
	'validation_exceptions': API_EXCEPTIONS,
	'allow_functions': app.config['API_ALLOW_FUNCTIONS'],
	'allow_patch_many': app.config['API_ALLOW_PATCH_MANY']}

classes = getmembers(modules[__name__], isclass)
api_classes = filter(lambda x: str(x[1]).startswith("<class 'app"), classes)
[mgr.create_api(eval(tuple[0]), **kwargs) for tuple in api_classes]
