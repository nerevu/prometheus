from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from wtforms.ext.dateutil.fields import DateField

class TypeForm(Form):
    name = TextField('Type Name', description='Type of event', validators=[Required()])
    unit = TextField('Unit', description='Unit of measurement', validators=[Required()])

class EventForm(Form):
    symbol = TextField('Symbol', description='Stock ticker symbol',
    	validators=[Required()])
    type_id = SelectField('Type', description='Type of event', coerce=int,
    	validators=[Required()])
    value = FloatField('Value', description='Amount the event was worth',
    	validators=[Required()])
    date = DateField('Date', description='Date the event happened',
    	validators=[Required()])
