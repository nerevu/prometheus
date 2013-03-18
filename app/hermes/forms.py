from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from wtforms.ext.dateutil.fields import DateField
from app.helper import get_choices, get_validators

univals = [Required()]


class CommodityForm(Form):
	symbol = TextField(
		'Ticker Symbol', description='Usually 3 or 4 letters',
		validators=univals)

	name = TextField('Name', description='Commodity name', validators=univals)
	type_id = SelectField(
		'Type', description='Type of commodity', coerce=int)
	data_source_id = SelectField(
		'Data Source', description='Data source', coerce=int)
	exchange_id = SelectField(
		'Exchange', description='Stock exchange', coerce=int)

	@classmethod
	def new(self):
		form = self()
		table = 'commodity_type'
		form.type_id.choices = get_choices(table, 'id', 'name', conn)
		form.type_id.validators = get_validators(table, 'id', conn)
		form.data_source_id.choices = get_choices(
			'data_source', 'id', conn, 'name')
		form.data_source_id.validators = get_validators('data_source', 'id')
		form.exchange_id.choices = get_choices('exchange', 'id', conn, 'symbol')
		form.exchange_id.validators = get_validators('exchange', 'id')
		return form


class EventTypeForm(Form):
	name = TextField('Name', description='Type of event', validators=univals)


class EventForm(Form):
	type_id = SelectField(
		'Event Type', description='Type of event', coerce=int)
	commodity_id = SelectField('Stock', description='Stock', coerce=int)
	currency_id = SelectField(
		'Currency', description='Unit the event is measured in', coerce=int)
	value = FloatField(
		'Value', description='Amount the event was worth', validators=univals)
	date = DateField(
		'Date', description='Date the event happened', validators=univals)

	@classmethod
	def new(self):
		form = self()
		table = 'commodity'
		kwargs = {'order': 'symbol', 'column': 'type_id', 'value': range(5)}
		form.commodity_id.choices = get_choices(table, 'id', conn, **kwargs)
		form.commodity_id.validators = get_validators(table, 'id')
		form.type_id.choices = get_choices('event_type', 'id', conn, 'name')
		form.type_id.validators = get_validators('event_type', 'id')
		kwargs.update({'value': [5, 6]})
		form.currency_id.choices = get_choices(table, 'id', conn, **kwargs)
		form.currency_id.validators = get_validators(table, 'id')
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
		table = 'commodity'
		kwargs = {'order': 'symbol', 'column': 'type_id', 'value': range(5)}
		form.commodity_id.choices = get_choices(table, 'id', conn, **kwargs)
		form.commodity_id.validators = get_validators(table, 'id')
		kwargs.update({'value': [5]})
		form.currency_id.choices = get_choices(table, 'id', conn, **kwargs)
		form.currency_id.validators = get_validators(table, 'id')
		return form
