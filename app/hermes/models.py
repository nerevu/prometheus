# from __future__ import print_function
import savalidation.validators as val

from pprint import pprint
from datetime import datetime as dt, date as d

from app import db

from savalidation import ValidationMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import backref


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
	if 'sqlite3' in str(dbapi_connection.cursor):
		"""Enable foreign key constraints for SQLite."""
		cursor = dbapi_connection.cursor()
		cursor.execute("PRAGMA foreign_keys=ON")
		cursor.close()


class Exchange(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	symbol = db.Column(db.String(12), unique=True, nullable=False)
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Exchange(%r, %r)>' % (self.symbol, self.name))


class DataSource(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<DataSource(%r)>' % self.name)


class CommodityGroup(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<CommodityGroup(%r)>' % self.name)


class CommodityType(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	group_id = db.Column(
		db.Integer, db.ForeignKey(
			'commodity_group.id', onupdate="CASCADE", ondelete="CASCADE"),
			nullable=False)
	group = db.relationship(
		'CommodityGroup', backref=backref('types',
		cascade='all, delete'), lazy='joined')

	# other keys
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<CommodityType(%r)>' % self.name)


class Commodity(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	type_id = db.Column(
		db.Integer, db.ForeignKey(
			'commodity_type.id', onupdate="CASCADE", ondelete="CASCADE"),
			nullable=False)
	type = db.relationship(
		'CommodityType', backref=backref('commodities',
		cascade='all, delete'), lazy='joined')

	data_source_id = db.Column(
		db.Integer, db.ForeignKey(
			'data_source.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	data_source = db.relationship(
		'DataSource', backref=backref('commodities',
		cascade='all, delete'), lazy='joined')

	exchange_id = db.Column(
		db.Integer, db.ForeignKey('exchange.id'), nullable=False)
	exchange = db.relationship(
		'Exchange', backref=backref('commodities',
		cascade='all, delete'), lazy='joined')

	# other keys
# 	cusip = db.Column(db.String(16), unique=True)
	symbol = db.Column(db.String(12), unique=True, nullable=False)
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Commodity(%r, %r)>' % (self.symbol, self.name))


class EventType(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	name = db.Column(db.String(64), nullable=False, unique=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return '<Type(%r)>' % (self.name)


class Event(db.Model, ValidationMixin):
	# table constraints
	__table_args__ = (
		db.UniqueConstraint(
			'commodity_id', 'date', 'type_id', 'currency_id'), {})

	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	commodity_id = db.Column(
		db.Integer, db.ForeignKey('commodity.id'), nullable=False)
	commodity = db.relationship(
		'Commodity', backref=backref('commodity_events',
		cascade='all, delete'), lazy='joined',
		primaryjoin='Commodity.id==Event.commodity_id')

	currency_id = db.Column(
		db.Integer, db.ForeignKey('commodity.id'), nullable=False)
	currency = db.relationship(
		'Commodity', backref=backref('currency_events', cascade='all, delete'),
		lazy='joined', primaryjoin='Commodity.id==Event.currency_id')

	type_id = db.Column(
		db.Integer, db.ForeignKey('event_type.id'), nullable=False)
	type = db.relationship(
		'EventType', backref=backref('events',
		cascade='all, delete'), lazy='joined')

	# other keys
	value = db.Column(db.Float, nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=d.today())

	# validation
	val.validates_constraints()

	def __repr__(self):
		return (
			'<Event(%r, %r, %r, %r)>' % (
				self.commodity_id, self.currency_id, self.value, self.date))


class Price(db.Model, ValidationMixin):
	# constraints
	__table_args__ = (
		db.UniqueConstraint('commodity_id', 'currency_id', 'date'), {})

	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	commodity_id = db.Column(
		db.Integer, db.ForeignKey('commodity.id'), nullable=False)
	commodity = db.relationship(
		'Commodity', backref=backref('commodity_prices',
		cascade='all, delete'), lazy='joined',
		primaryjoin='Commodity.id==Price.commodity_id')

	currency_id = db.Column(
		db.Integer, db.ForeignKey('commodity.id'), nullable=False)
	currency = db.relationship(
		'Commodity', backref=backref('currency_prices',
		cascade='all, delete'), lazy='joined',
		primaryjoin='Commodity.id==Price.currency_id')

	# other keys
	close = db.Column(db.Float, nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=d.today())

	# validation
	val.validates_constraints()

	def __repr__(self):
		return (
			'<Price(%r, %r, %r, %r)>' % (
				self.close, self.commodity_id, self.currency_id, self.date))
