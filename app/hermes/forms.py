from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from flask.ext.wtf import AnyOf
from wtforms.ext.dateutil.fields import DateField
from .models import EventType, Commodity, CommodityType, Exchange, DataSource

univals = [Required()]


def _get_choices(a_class, value_field, *args, **kwargs):
	order = '%s.%s' % (a_class.__table__, args[0])

	try:
		filter = '%s.%s' % (a_class.__name__, kwargs['column'])
		value = kwargs['value']
		result = a_class.query.filter(eval(filter).in_(value)).order_by(order).all()
	except KeyError:
		result = a_class.query.order_by(order).all()

	values = [getattr(x, value_field) for x in result]
	combo = []

	for arg in args:
		try:
			new = [getattr(getattr(x, arg[0]), arg[1]) for x in result]
		except Exception:
			new = [getattr(x, arg) for x in result]

		combo.append(new)

	try:
# 		attr = map(lambda x, y: ', '.join([x, y]), combo[0], combo[1])
		attr = [', '.join(x) for x in zip(combo[0], combo[1])]
	except IndexError:
		attr = combo[0]

	return zip(values, attr)


def _get_validators(a_class, value_field):
	result = a_class.query.all()
	values = [getattr(x, value_field) for x in result]
	values = sorted(values)
	return [
		Required(), AnyOf(
			values, message=u'Invalid value, must be one of:'
			'%(values)s')]


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
		form.type_id.choices = _get_choices(a_class, 'id', 'name')
		form.type_id.validators = _get_validators(a_class, 'id')
		form.data_source_id.choices = _get_choices(DataSource, 'id', 'name')
		form.data_source_id.validators = _get_validators(DataSource, 'id')
		form.exchange_id.choices = _get_choices(Exchange, 'id', 'symbol')
		form.exchange_id.validators = _get_validators(Exchange, 'id')
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
		form.commodity_id.choices = _get_choices(a_class, 'id', args, **kwargs)
		form.commodity_id.validators = _get_validators(a_class, 'id')
		form.type_id.choices = _get_choices(EventType, 'id', 'name')
		form.type_id.validators = _get_validators(EventType, 'id')
		kwargs = {'column': 'type_id', 'value': [5, 6]}
		form.currency_id.choices = _get_choices(a_class, 'id', args, **kwargs)
		form.currency_id.validators = _get_validators(a_class, 'id')
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
		form.commodity_id.choices = _get_choices(a_class, 'id', args, **kwargs)
		form.commodity_id.validators = _get_validators(a_class, 'id')
		kwargs = {'column': 'type_id', 'value': [5]}
		form.currency_id.choices = _get_choices(a_class, 'id', args, **kwargs)
		form.currency_id.validators = _get_validators(a_class, 'id')
		return form
