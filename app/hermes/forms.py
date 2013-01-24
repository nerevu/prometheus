from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from flask.ext.wtf import AnyOf
from wtforms.ext.dateutil.fields import DateField
from app.form_helper import get_choices, get_validators
from .models import EventType, Commodity, CommodityType, Exchange, DataSource

univals = [Required()]


class CommodityForm(Form):
# 	cusip = TextField('CUSIP', description='CUSIP')
	symbol = TextField(
		'Ticker Symbol', description='Usually 3 or 4 letters',
		validators=univals)

	name = TextField('Name', description='Commodity Name', validators=univals)
	type_id = SelectField(
		'Type', description='Type of Commodity', coerce=int)
	data_source_id = SelectField(
		'Data Source', description='Type of Commodity', coerce=int)
	exchange_id = SelectField(
		'Exchange', description='Type of Commodity', coerce=int)

	@classmethod
	def new(self):
		form = self()
		a_class = CommodityType
		form.type_id.choices = get_choices(a_class, 'id', 'name')
		form.type_id.validators = get_validators(a_class, 'id')
		form.data_source_id.choices = get_choices(DataSource, 'id', 'name')
		form.data_source_id.validators = get_validators(DataSource, 'id')
		form.exchange_id.choices = get_choices(Exchange, 'id', 'symbol')
		form.exchange_id.validators = get_validators(Exchange, 'id')
		return form


class EventTypeForm(Form):
	name = TextField('Name', description='Type of event', validators=univals)


class EventForm(Form):
	commodity_id = SelectField('Stock', description='Stock', coerce=int)
	type_id = SelectField(
		'Event Type', description='Type of event', coerce=int)
	currency_id = SelectField(
		'Currency', description='Unit the event is measured in', coerce=int)
	value = FloatField(
		'Value', description='Amount the event was worth', validators=univals)
	date = DateField(
		'Date', description='Date the event happened', validators=univals)

	@classmethod
	def new(self):
		form = self()
		a_class = Commodity
		args = 'symbol'
		kwargs = {'column': 'type_id', 'value': range(5)}
		form.commodity_id.choices = get_choices(a_class, 'id', args, **kwargs)
		form.commodity_id.validators = get_validators(a_class, 'id')
		form.type_id.choices = get_choices(EventType, 'id', 'name')
		form.type_id.validators = get_validators(EventType, 'id')
		kwargs = {'column': 'type_id', 'value': [5, 6]}
		form.currency_id.choices = get_choices(a_class, 'id', args, **kwargs)
		form.currency_id.validators = get_validators(a_class, 'id')
		return form


class PriceForm(Form):
	commodity_id = SelectField('Stock', description='Stock', coerce=int)
	currency_id = SelectField(
		'Currency', description='Currency the price is in', coerce=int)

	close = FloatField(
		'Closing Price', description='End of day closing price',
		validators=univals)

	date = DateField('Date', description='Closing date', validators=univals)

	@classmethod
	def new(self):
		form = self()
		a_class = Commodity
		args = 'symbol'
		kwargs = {'column': 'type_id', 'value': range(5)}
		form.commodity_id.choices = get_choices(a_class, 'id', args, **kwargs)
		form.commodity_id.validators = get_validators(a_class, 'id')
		kwargs = {'column': 'type_id', 'value': [5]}
		form.currency_id.choices = get_choices(a_class, 'id', args, **kwargs)
		form.currency_id.validators = get_validators(a_class, 'id')
		return form
