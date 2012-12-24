from itertools import imap, repeat
from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from flask.ext.wtf import AnyOf
from wtforms.ext.dateutil.fields import DateField
from .models import EventType, Commodity

univals = [Required()]


def _get_choices(a_class, value_field, *args):
	order = '%s.%s' % (a_class.__table__, args[0])
	result = a_class.query.order_by(order).all()
	values = [getattr(x, value_field) for x in result]
	combo = []

	for arg in args:
		try:
			new = [getattr(getattr(x, arg[0]), arg[1]) for x in result]
		except:
			new = [getattr(x, arg) for x in result]

		combo.append(new)

	try:
		attr = map(lambda x, y: ', '.join([x, y]), combo[0], combo[1])
	except IndexError:
		attr = combo[0]

	choices = map(lambda x, y: (x, y), values, attr)
	return choices


def _get_validators(a_class, value_field):
	result = a_class.query.all()
	values = [getattr(x, value_field) for x in result]
	values = sorted(values)
	return [Required(), AnyOf(values, message=u'Invalid value, must be one of:'
		'%(values)s')]


class CommodityForm(Form):
# 	cusip = TextField('CUSIP', description='CUSIP')
	symbol = TextField('Ticker Symbol', description='Usually 3 or 4 letters',
		validators=univals)
	name = TextField('Name', description='Commodity Name', validators=univals)


class EventTypeForm(Form):
	name = TextField('Name', description='Type of event',
		validators=univals)
	commodity_id = SelectField('Unit', description='Unit of measurement',
		coerce=int)

	@classmethod
	def new(cls):
		form = cls()
		form.commodity_id.choices = _get_choices(Commodity, 'id', 'symbol')
		form.commodity_id.validators = _get_validators(Commodity, 'id')
		return form


class EventForm(Form):
	symbol = TextField('Symbol', description='Ticker symbol',
		validators=univals)
	event_type_id = SelectField('Event Type', description='Type of event',
		coerce=int)
	value = FloatField('Value', description='Amount the event was worth',
		validators=univals)
	date = DateField('Date', description='Date the event happened',
		validators=univals)

	@classmethod
	def new(cls):
		form = cls()
		form.event_type_id.choices = _get_choices(EventType, 'id', 'name',
			['unit', 'symbol'])
		form.event_type_id.validators = _get_validators(EventType, 'id')
		return form


class PriceForm(Form):
	commodity_id = SelectField('Stock', description='Stock', coerce=int)
	currency_id = SelectField('Currency',
		description='Currency the price is in', coerce=int)
	close = FloatField('Closing Price', description='End of day closing price',
		validators=univals)
	date = DateField('Date', description='Closing date', validators=univals)

	@classmethod
	def new(cls):
		form = cls()
		form.commodity_id.choices = _get_choices(Commodity, 'id', 'symbol')
		form.commodity_id.validators = _get_validators(Commodity, 'id')
		form.currency_id.choices = _get_choices(Commodity, 'id', 'symbol')
		form.currency_id.validators = _get_validators(Commodity, 'id')
		return form
