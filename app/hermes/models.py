# from __future__ import print_function
from pprint import pprint
import savalidation.validators as val

from datetime import datetime as dt, date as d
from json import dumps as dmp
from requests import post
from app import db
from savalidation import ValidationMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import backref


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
	"""Enable foreign key constraints for SQLite."""
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()


def init_db(site):
	hdr = {'content-type': 'application/json'}

	content = [{'table': 'exchange',
	'data': [{'symbol': 'NYSE', 'name': 'New York Stock Exchange'},
		{'symbol': 'NASDAQ', 'name': 'NASDAQ'},
		{'symbol': 'OTC', 'name': 'Over the counter'},
		{'symbol': 'N/A', 'name': 'Currency'}]},

	{'table': 'data_source',
	'data': [{'name': 'Yahoo'}, {'name': 'Google'}, {'name': 'XE'}]},

	{'table': 'commodity_group',
	'data': [{'name': 'Security'}, {'name': 'Currency'}, {'name': 'Other'}]},

	{'table': 'commodity_type',
	'data': [{'name': 'Stock', 'group_id': 1},
		{'name': 'Bond', 'group_id': 1},
		{'name': 'Mutual Fund', 'group_id': 1},
		{'name': 'ETF', 'group_id': 1},
		{'name': 'Currency', 'group_id': 2},
		{'name': 'Descriptor', 'group_id': 3}]},

	{'table': 'commodity',
	'data': [{'symbol': 'USD', 'name': 'US Dollar',
			'type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
		{'symbol': 'EUR', 'name': 'Euro',
			'type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
		{'symbol': 'GBP', 'name': 'Pound Sterling',
			'type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
		{'symbol': 'TZS', 'name': 'Tanzanian Shilling',
			'type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
		{'symbol': 'Multiple', 'name': 'Multiple',
			'type_id': 6, 'data_source_id': 3, 'exchange_id': 4},
		{'symbol': 'Text', 'name': 'Text',
			'type_id': 6, 'data_source_id': 3, 'exchange_id': 4}]},

	{'table': 'event_type',
	'data': [{'name': 'Dividend', 'commodity_id': '1'},
		{'name': 'Special Dividend', 'commodity_id': '1'},
		{'name': 'Stock Split', 'commodity_id': '5'},
		{'name': 'Name Change', 'commodity_id': '6'},
		{'name': 'Ticker Change', 'commodity_id': '6'}]}]

	for dict in content:
		table = dict['table']
		data = dict['data']
		[post('%s/%s' % (site, table), data=dmp(d), headers=hdr) for d in data]


def pop_db(site):
	pass


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
	group_id = db.Column(db.Integer,
		db.ForeignKey('commodity_group.id', onupdate="CASCADE",
		ondelete="CASCADE"), nullable=False)
	group = db.relationship('CommodityGroup', backref=backref('types',
		cascade='all, delete'), lazy='joined')

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
	type_id = db.Column(db.Integer,
		db.ForeignKey('commodity_type.id', onupdate="CASCADE",
		ondelete="CASCADE"), nullable=False)
	type = db.relationship('CommodityType', backref=backref('commodities',
		cascade='all, delete'), lazy='joined')
	data_source_id = db.Column(db.Integer,
		db.ForeignKey('data_source.id', onupdate="CASCADE",
		ondelete="CASCADE"), nullable=False)
	data_source = db.relationship('DataSource', backref=backref('commodities',
		cascade='all, delete'), lazy='joined')
	exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'),
		nullable=False)
	exchange = db.relationship('Exchange', backref=backref('commodities',
		cascade='all, delete'), lazy='joined')

	# validation
	val.validates_constraints()

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
	unit = db.relationship('Commodity', backref=backref('event_types',
		cascade='all, delete'), lazy='joined')

	# validation
	val.validates_constraints()

	def __repr__(self):
		return '<Type(%r, %r)>' % (self.name, self.commodity_id)


class Event(db.Model, ValidationMixin):
	__table_args__ = (db.UniqueConstraint('symbol', 'date', 'type_id',
		'value'), {})

	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	symbol = db.Column(db.String(12), nullable=False)
	value = db.Column(db.Float, nullable=False)
	type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'),
		nullable=False)
	type = db.relationship('EventType', backref=backref('events',
		cascade='all, delete'), lazy='joined')
	date = db.Column(db.Date, nullable=False, default=d.today())

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Event(%r, %r, %r, %r)>'
			% (self.symbol, self.value, self.type_id, self.date))


class Price(db.Model, ValidationMixin):
	__table_args__ = (db.UniqueConstraint('commodity_id', 'currency_id',
		'date'), {})

	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(db.DateTime, nullable=False, default=dt.utcnow(),
		onupdate=dt.utcnow())

	commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'),
		nullable=False)
	commodity = db.relationship('Commodity', backref=backref('commodity_prices',
		cascade='all, delete'), lazy='joined',
		primaryjoin='Commodity.id==Price.commodity_id')
	currency_id = db.Column(db.Integer, db.ForeignKey('commodity.id'),
		nullable=False)
	currency = db.relationship('Commodity', backref=backref('currency_prices',
		cascade='all, delete'), lazy='joined',
		primaryjoin='Commodity.id==Price.currency_id')
	date = db.Column(db.Date, nullable=False, default=d.today())
	close = db.Column(db.Float, nullable=False)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Price(%r, %r, %r, %r)>'
			% (self.close, self.commodity_id, self.currency_id, self.date))
