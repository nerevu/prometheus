# -*- coding: utf-8 -*-
"""
	app.hermes
	~~~~~~~~~~~~~~

	Provides application price and event aggregation functions
"""

from app import db
from sqlalchemy.orm import aliased
from .models import Event, EventType, Price, Commodity, CommodityType


def get_table_info(table):
	def get_event():
		form_fields = ['commodity_id', 'type_id', 'currency_id', 'value',
			'date']
		table_headers = ['Symbol', 'Name', 'Unit', 'Value', 'Date']
		Currency = aliased(Commodity)
		query = (db.session.query(Event, EventType, Commodity, Currency)
			.join(EventType).join(Event.commodity)
			.join(Currency, Event.currency).order_by(Event.date))
		data_fields = [(2, 'symbol'), (1, 'name'), (3, 'symbol'),
			(0, 'value'), (0, 'date')]
		return form_fields, table_headers, query, data_fields

	def get_event_type():
		form_fields = ['name']
		table_headers = ['Type Name']
		query = db.session.query(EventType).order_by(EventType.name)
		data_fields = ['name']
		return form_fields, table_headers, query, data_fields

	def get_price():
		form_fields = ['commodity_id', 'currency_id', 'close', 'date']
		table_headers = ['Stock', 'Currency', 'Date', 'Price']
		Currency = aliased(Commodity)
		query = (db.session.query(Price, Commodity, Currency)
			.join(Price.commodity).join(Currency, Price.currency)
			.order_by(Price.date))
		data_fields = [(1, 'symbol'), (2, 'symbol'), (0, 'date'), (0, 'close')]
		return form_fields, table_headers, query, data_fields

	def get_commodity():
		form_fields = ['symbol', 'name', 'type_id', 'data_source_id',
			'exchange_id']
		table_headers = ['Symbol', 'Name', 'Type']
		query = (db.session.query(Commodity, CommodityType).join(CommodityType)
			.order_by(Commodity.name))
		data_fields = [(0, 'symbol'), (0, 'name'), (1, 'name')]
		return form_fields, table_headers, query, data_fields

	switch = {'event': get_event(),
		'event_type': get_event_type(),
		'price': get_price(),
		'commodity': get_commodity()}

	return switch.get(table)


def get_plural(word):
	if word[-1] == 'y':
		return word[:-1] + 'ies'
	else:
		return word + 's'
