from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField, AnyOf
from wtforms.ext.dateutil.fields import DateField
from .models import EventType

def _get_choices(a_class, value_field, *args):
	result = a_class.query.order_by('name').all()
	return [(getattr(x, value_field), '%s' % ', '.join(args).title()) for x in result]

def _get_validators(a_class, value_field):
	result = a_class.query.order_by('name').all()
	values = [getattr(x, value_field) for x in result]
	values = sorted(values)
	return [Required(), AnyOf(values, message=u'Invalid value, must be one of: %(values)s')]

class CommodityForm(Form):
	cusip = TextField('CUSIP', description='Stock CUSIP', validators=[Required()])
	symbol = TextField('Ticker Symbol', description='Usually 3 or 4 letters', validators=[Required()])
	name = TextField('Stock Name', description='Stock Name', validators=[Required()])

class EventTypeForm(Form):
	name = TextField('Type Name', description='Type of event', validators=[Required()])
	unit = TextField('Unit', description='Unit of measurement', validators=[Required()])

class EventForm(Form):
	symbol = TextField('Symbol', description='Stock ticker symbol',
		validators=[Required()])
	event_type_id = SelectField('Event Type', description='Type of event',
		coerce=int)
	value = FloatField('Value', description='Amount the event was worth',
		validators=[Required()])
	date = DateField('Date', description='Date the event happened',
		validators=[Required()])

	@classmethod
	def new(cls):
		form = cls()
		form.event_type_id.choices = _get_choices(
			EventType, 'id', 'name', 'unit')

		form.event_type_id.validators = _get_validators(EventType, 'id')
		return form

class PriceForm(Form):
	commodity_id = SelectField('Stock', description='Stock', coerce=int)
	currency_id = SelectField('Currency', description='Currency the price is in'
		, coerce=int)
	close = FloatField('Close', description='End of day closing price',
		validators=[Required()])
	date = DateField('Date', description='Closing date',
		validators=[Required()])

	@classmethod
	def new(cls):
		form = cls()
		form.commodity_id.choices = _get_choices(Commodity, 'id', 'Symbol')
		form.commodity_id.validators = _get_validators(Commodity, 'id')
		form.currency_id.choices = _get_choices(Commodity, 'id', 'Symbol')
		form.currency_id.validators = _get_validators(Commodity, 'id')
		return form
