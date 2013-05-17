from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from flask.ext.wtf import BooleanField
from flask import current_app as app
from wtforms.ext.dateutil.fields import DateField
from app.helper import HelpForm, app_site

univals = [Required()]


def help():
	with app.app_context():
		return HelpForm(app_site())


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
		helper = help()
		tables = ['holding', 'commodity']
		fields = ['id', 'symbol']
		form.holding_id.choices = helper.get_x_choices(tables, fields)
		form.holding_id.validators = helper.get_validators('holding', 'id')
		form.type_id.choices = helper.get_choices('trxn_type', 'id', 'name')
		form.type_id.validators = helper.get_validators('holding', 'id')
		return form


class TrxnUploadForm(Form):
	name = TextField('Name', description='File name', validators=univals)
