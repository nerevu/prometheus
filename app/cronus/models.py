# from __future__ import print_function
import savalidation.validators as val

from pprint import pprint
from datetime import datetime as dt, date as d

from app import db
from app.hermes.models import Commodity

from savalidation import ValidationMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref


class Person(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	currency_id = db.Column(
		db.Integer, db.ForeignKey(
			'commodity.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	currency = db.relationship(
		'Commodity', lazy='joined',
		backref=backref('people', cascade='all, delete'))

	# other keys
	first_name = db.Column(db.Unicode(64), nullable=False)
	last_name = db.Column(db.Unicode(64), nullable=False)
	email = db.Column(db.String(64), unique=True, nullable=False)
	phone = db.Column(db.String(16))
	birth_date = db.Column(db.Date)
	monthly_income = db.Column(db.Float)
	monthly_expenses = db.Column(db.Float)
	marginal_tax_rate = db.Column(db.Float)

	# validation
	val.validates_email('email')
	val.validates_constraints()

	def __repr__(self):
		return ('<Exchange(%r, %r)>' % (self.name, self.email))

	def __str__(self):
		return ('%s: %s' % (self.name, self.email))


class Company(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	name = db.Column(db.String(64), unique=True, nullable=False)
	website = db.Column(db.String(64), unique=True, nullable=False)
	phone = db.Column(db.String(16))
	address = db.Column(db.String(64))
	city = db.Column(db.String(16))
	state = db.Column(db.String(2))
	zip = db.Column(db.String(10))

	# validation
	val.validates_url('website')
	val.validates_constraints()

	def __repr__(self):
		return ('<Exchange(%r, %r)>' % (self.name, self.email))

	def __str__(self):
		return ('%s: %s' % (self.name, self.email))


class AccountType(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	name = db.Column(db.String(64), unique=True, nullable=False)
	contribution_limit = db.Column(db.Float)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<AccountType(%r)>' % self.name)

	def __str__(self):
		return ('%s' % self.name)


class TrxnType(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# other keys
	name = db.Column(db.String(64), unique=True, nullable=False)
	description = db.Column(db.String(256))

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<TrxnType(%r)>' % self.name)

	def __str__(self):
		return ('%s' % self.name)


class Account(db.Model, ValidationMixin):
	# constraints
	__table_args__ = (
		db.UniqueConstraint(
			'name', 'type_id', 'company_id', 'currency_id', 'owner_id'), {})

	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	type_id = db.Column(
		db.Integer, db.ForeignKey(
			'account_type.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	type = db.relationship(
		'AccountType', lazy='joined',
		backref=backref('accounts', cascade='all, delete'))

	company_id = db.Column(
		db.Integer, db.ForeignKey(
			'company.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	company = db.relationship(
		'Company', lazy='joined',
		backref=backref('accounts', cascade='all, delete'))

	currency_id = db.Column(
		db.Integer, db.ForeignKey(
			'commodity.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	currency = db.relationship(
		'Commodity', lazy='joined',
		backref=backref('accounts', cascade='all, delete'))

	owner_id = db.Column(
		db.Integer, db.ForeignKey(
			'person.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	owner = db.relationship(
		'Person', lazy='joined',
		backref=backref('accounts', cascade='all, delete'))

	# other keys
	name = db.Column(db.String(64), unique=True, nullable=False)
	min_balance = db.Column(db.Float)
	trade_commission = db.Column(db.Float)
	annual_fee = db.Column(db.Float)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Account(%r)>' % self.name)

	def __str__(self):
		return ('%s' % self.name)


class Contribution(db.Model, ValidationMixin):
	# constraints
	__table_args__ = (db.UniqueConstraint('account_id', 'date'), {})

	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	account_id = db.Column(
		db.Integer, db.ForeignKey(
			'account.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	account = db.relationship(
		'Account', lazy='joined',
		backref=backref('contributions', cascade='all, delete'))

	# other keys
	amount = db.Column(db.Float, nullable=False)
	date = db.Column(db.Date, nullable=False)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Contribution(%r, %r)>' % (self.account, self.amount))

	def __str__(self):
		return ('%s: %s' % (self.account, self.amount))


class Holding(db.Model, ValidationMixin):
	# constraints
	__table_args__ = (db.UniqueConstraint('account_id', 'commodity_id'), {})

	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	account_id = db.Column(
		db.Integer, db.ForeignKey(
			'account.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	account = db.relationship(
		'Account', lazy='joined',
		backref=backref('holdings', cascade='all, delete'))

	commodity_id = db.Column(
		db.Integer, db.ForeignKey(
			'commodity.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	commodity = db.relationship(
		'Commodity', lazy='joined',
		backref=backref('holdings', cascade='all, delete'))

	# other keys
	description = db.Column(db.String(256))

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Holding(%r, %r)>' % (self.account_id, self.commodity_id))

	def __str__(self):
		return ('%s: %s' % (self.account, self.commodity))


class Transaction(db.Model, ValidationMixin):
	# auto keys
	id = db.Column(db.Integer, primary_key=True)
	utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
	utc_updated = db.Column(
		db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

	# foreign keys
	type_id = db.Column(
		db.Integer, db.ForeignKey(
			'trxn_type.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	type = db.relationship(
		'TrxnType', lazy='joined',
		backref=backref('transactions', cascade='all, delete'))

	holding_id = db.Column(
		db.Integer, db.ForeignKey(
			'holding.id', onupdate="CASCADE", ondelete="CASCADE"),
		nullable=False)
	holding = db.relationship(
		'Holding', lazy='joined',
		backref=backref('transactions', cascade='all, delete'))

	# other keys
	shares = db.Column(db.Float, nullable=False)
	price = db.Column(db.Float, nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=d.today())
	commissionable = db.Column(db.Boolean, nullable=False, default=True)

	# validation
	val.validates_constraints()

	def __repr__(self):
		return ('<Holding(%r, %r)>' % (self.type_id, self.holding_id))

	def __str__(self):
		return ('%s: %s' % (self.type, self.holding))
