from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from flask.ext.wtf import AnyOf, BooleanField
from wtforms.ext.dateutil.fields import DateField
from app.helper import get_choices, get_validators
from .models import Holding, TrxnType

univals = [Required()]


class TransactionForm(Form):
	holding_id = SelectField(
		'Holding', description='Commodity holding', coerce=int)
	type_id = SelectField(
		'Type', description='Type of transaction', coerce=int)
	shares = FloatField(
		'Shares', description='Number of shares', validators=univals)
	price = FloatField(
		'Share Price', description='Price per share', validators=univals)
	date = DateField(
		'Date', description='Date the event happened', validators=univals)
	commissionable = BooleanField(
		'Commissionable', description='Were commissions paid?')

	@classmethod
	def new(self):
		form = self()
		a_class = Holding
		form.holding_id.choices = get_choices(a_class, 'id', 'commodity_id')
		form.holding_id.validators = get_validators(a_class, 'id')
		form.type_id.choices = get_choices(TrxnType, 'id', 'name')
		form.type_id.validators = get_validators(a_class, 'id')
		return form
