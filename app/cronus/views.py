# from __future__ import print_function
from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for

from app.connection import Connection, portify
from app.view_helper import get_kwargs
from .forms import TransactionForm
from .models import Transaction

cronus = Blueprint('cronus', __name__)
table = 'transaction'


@cronus.route('/transaction/', methods=['GET', 'POST'])
def transaction():
	site = portify(url_for('api', _external=True))
	conn = Connection(site, display=True)
	kwargs = get_kwargs(str(table), 'cronus', conn, False)
	return render_template('entry.html', **kwargs)


@cronus.route('/add_trxn/', methods=['GET', 'POST'])
def add():
	pass
