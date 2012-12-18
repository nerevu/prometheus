from flask.ext.wtf import Form, TextField, FloatField, Required, SelectField
from wtforms.ext.dateutil.fields import DateField

class TypeForm(Form):
    name = TextField('Name', [Required()])
    unit = TextField('Unit', [Required()])

class EventForm(Form):
    symbol = TextField('Symbol', description='Stock ticker symbol')
    type_id = SelectField('Type', description='Type of event', coerce=int)
    value = FloatField('Value', description='Amount the event was worth')
    date = DateField(u'Date', description='Date the event happened')
