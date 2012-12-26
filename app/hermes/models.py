# from __future__ import print_function
import savalidation.validators as val

from datetime import datetime as dt, date as d

from app import db
from savalidation import ValidationMixin
from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy.schema import UniqueConstraint


class Exchange(db.Model, ValidationMixin):
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())
	symbol = db.Column(db.String(12), unique=True, nullable=False)
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Exchange(%r, %r)>' % (self.symbol, self.name))


class DataSource(db.Model, ValidationMixin):
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())
	name = db.Column(db.String(64), nullable=False, unique=True)

	val.validates_constraints()

	def __repr__(self):
		return ('<DataSource(%r)>' % self.name)


class CommodityGroup(db.Model, ValidationMixin):
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())
	name = db.Column(db.String(64), nullable=False, unique=True)

	val.validates_constraints()

	def __repr__(self):
		return ('<CommodityGroup(%r)>' % self.name)


class CommodityType(db.Model, ValidationMixin):
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())
	name = db.Column(db.String(64), nullable=False, unique=True)
	commodity_group_id = db.Column(db.Integer,
		db.ForeignKey('commodity_group.id'), nullable=False)
	group = db.relationship('CommodityGroup', backref='commodity_types',
		lazy='joined')

	val.validates_constraints()

	def __repr__(self):
		return ('<CommodityType(%r)>' % self.name)


class Commodity(db.Model, ValidationMixin):
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

# 	cusip = db.Column(db.String(16), unique=True)
	symbol = db.Column(db.String(12), unique=True, nullable=False)
	name = db.Column(db.String(64), nullable=False, unique=True)
	commodity_type_id = db.Column(db.Integer,
		db.ForeignKey('commodity_type.id'), nullable=False)
	type = db.relationship('CommodityType', backref='commodities',
		lazy='joined')
	data_source_id = db.Column(db.Integer,
		db.ForeignKey('data_source.id'), nullable=False)
	data_source = db.relationship('DataSource', backref='commodities',
		lazy='joined')
	exchange_id = db.Column(db.Integer,
		db.ForeignKey('exchange.id'), nullable=False)
	exchange = db.relationship('Exchange', backref='commodities', lazy='joined')

	# validation
	val.validates_constraints()

# 	def __init__(self, symbol=None, name=None):
# 		self.symbol = symbol
# 		self.name = name

	def __repr__(self):
		return ('<Commodity(%r, %r)>' % (self.symbol, self.name))


class EventType(db.Model, ValidationMixin):
	__table_args__ = (db.UniqueConstraint('name', 'commodity_id'), {})
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	name = db.Column(db.String(64), nullable=False)
	commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'),
		nullable=False)
	unit = db.relationship('Commodity', backref='event_types', lazy='joined')

	# validation
	val.validates_constraints()

# 	def __init__(self, name=None, commodity_id=None):
# 		self.name = name
# 		self.commodity_id = commodity_id

	def __repr__(self):
		return '<Type(%r, %r)>' % (self.name, self.commodity_id)


class Event(db.Model, ValidationMixin):
	__table_args__ = (db.UniqueConstraint('symbol', 'date', 'event_type_id',
		'value'), {})

	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	symbol = db.Column(db.String(12), nullable=False)
	value = db.Column(db.Float, nullable=False)
	event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'),
		nullable=False)
	type = db.relationship('EventType', backref='events', lazy='joined')
	date = db.Column(db.Date, nullable=False, default=d.today())

	# validation
	val.validates_constraints()

# 	def __init__(self, symbol=None, value=None, type=None, event_type_id=None,
# 		date=None):
#
# 		self.symbol = symbol
# 		self.value = value
# 		self.event_type_id = event_type_id
# 		self.type = type
# 		self.date = (date or d.today())

	def __repr__(self):
		return ('<Event(%r, %r, %r, %r)>'
			% (self.symbol, self.value, self.event_type_id, self.date))


class Price(db.Model, ValidationMixin):
	__table_args__ = (db.UniqueConstraint('commodity_id', 'currency_id',
		'date'), {})

	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'),
		nullable=False)
	commodity = db.relationship('Commodity', backref='commodity_prices',
		lazy='joined', primaryjoin='Commodity.id==Price.commodity_id')
	currency_id = db.Column(db.Integer, db.ForeignKey('commodity.id'),
		nullable=False)
	currency = db.relationship('Commodity', backref='currency_prices',
		lazy='joined', primaryjoin='Commodity.id==Price.currency_id')
	date = db.Column(db.Date, nullable=False, default=d.today())
	close = db.Column(db.Float, nullable=False)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Price(%r, %r, %r, %r)>'
			% (self.close, self.commodity_id, self.currency_id, self.date))
