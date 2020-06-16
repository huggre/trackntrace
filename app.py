# Import some Iota interact functions
from iota_interact import send_transaction
from iota_interact import get_transactions
from iota_interact import GenerateAddressFromBarcode

# Import datetime libary
import time
import datetime

# Import json
import json

# Import hashlib
import hashlib

from random import randint
from time import strftime
from flask import Flask, redirect, url_for, render_template, flash, request, jsonify
from wtforms import Form, SelectField, TextField, TextAreaField, validators, StringField, SubmitField

# Imports IotaGo form dependencies
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

# Import Flask-WTF
from flask_wtf import FlaskForm

# Import Flask Bootstrap
from flask_bootstrap import Bootstrap

# Define full node to be used when uploading/downloading transaction records to/from the tangle
# NodeURL = "https://nodes.thetangle.org:443"

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

# Create bootstrap object
bootstrap = Bootstrap(app)

class ReusableForm(FlaskForm):
    #actor_name = SelectField('Actor Name', choices=[('Hotel IOTA', 'Hotel IOTA'), ('Ben the Fisherman', 'Ben the Fisherman')])
    dropdown_list = ['Air', 'Land', 'Sea'] # You can get this from your model
    actor_name = SelectField('Actor Name', choices=dropdown_list, default=1)
    name = TextField('Name:', validators=[validators.required()])
    surname = TextField('Surname:', validators=[validators.required()])
    submit = SubmitField('Submit')

# Form for Register new transaction
class RegisterTransactionForm(FlaskForm):
    actor_name = SelectField('Actor Name', coerce=str)
    actor_key = StringField('Actor key', validators=[DataRequired()])
    transaction_type = RadioField('Transaction Type', choices=[('1','Inbound'),('2','Outbound')], default=1, coerce=str)
    barcode = StringField('Barcode', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form for displaying transaction history
class DisplayTransactionHistoryForm(FlaskForm):
    barcode = StringField('Barcode', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form for creating new barcodes
class CreateBarcodeForm(FlaskForm):
    barcode = StringField('Barcode', validators=[DataRequired()])
    submit = SubmitField('Submit')

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(name, surname, email):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Name={}, Surname={}, Email={} \n'.format(timestamp, name, surname, email))
    data.close()

# Function for hashing a string
def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

@app.route("/")
def index():

    return render_template('index.html')


# Create barcode
@app.route('/create_barcode', methods=['GET', 'POST'])
def create_barcode():

    form = CreateBarcodeForm()
    
    if form.validate_on_submit():
        print("hei")
        #tag = tbl_tags()
        #retval = save_tag(tag, form, new=True)
        #if retval == True:
        #    flash('New tag created sucessfully!!')
        #    return redirect(display_barcode.html)
    return render_template('create_barcode.html', title='Create barcode', form=form)


# Register transaction
@app.route('/register_transaction', methods=['GET', 'POST'])
def register_transaction():

    form = RegisterTransactionForm()
    
    form.actor_name.choices = [('1', 'Hotel IOTA Purchasing Dep.'), ('2', 'Bob the fisherman'), ('3', 'Trucks R Us'), ('4', 'SeaTrans Inc.'), ('5', 'WeDeliver Inc.'), ('6', 'Hotel IOTA Warehouse')]
    
    if form.validate_on_submit():
        
        # Get values from form
        actor_name = dict(form.actor_name.choices).get(form.actor_name.data)
        hash_string = 
        actor_key = form.actor_key.data
        transaction_type = dict(form.transaction_type.choices).get(form.transaction_type.data)
        barcode_ID = form.barcode.data

        # Create string to be hashed
        hash_string = barcode_ID + actor_key + transaction_type

        # Create a sha256 signature from the hash_string
        signature = encrypt_string(hash_string)

        # Get IOTA address from 13 digit barcode
        addr = GenerateAddressFromBarcode(barcode_ID)
        
        # Get current time
        timestamp = strftime("%Y-%m-%dT%H:%M")
        
        # Create upload json
        udata = {'timestamp' : timestamp, 'actor_name' : actor_name, 'transaction_type' : transaction_type, 'signature' : signature}
        msg = json.dumps(udata)
        
        # Send transaction to the IOTA tangle
        send_transaction(actor_seed, addr, msg)

        # Show confirmation that new transaction was sendt
        flash('New transaction registered to address: ' + str(addr))

    return render_template('register_transaction.html', title='Register transaction', form=form)

# Display transaction history input form
@app.route('/display_transaction_history', methods=['GET', 'POST'])
def display_transaction_history():

    form = DisplayTransactionHistoryForm()

    if form.validate_on_submit():

        # Get barcode ID from form
        barcode_ID = form.barcode.data
        
        # Get transaction data from the IOTA tangle
        transactions = get_transactions(barcode_ID)

        # Show transaction history in new page
        return display_transaction_history_result(barcode_ID, transactions)

    return render_template('display_transaction_history.html', title='Display transaction history', form=form)


# Display transaction history result
@app.route('/display_transaction_history_result')
def display_transaction_history_result(barcode_ID, transactions):

    # Get IOTA address from 13 digit barcode
    addr = GenerateAddressFromBarcode(barcode_ID)

    # Create Address link
    addr_link = 'https://utils.iota.org/address/%s' % addr

    print(addr_link)

    return render_template('test.html', title='Transaction history', barcode_ID=barcode_ID, addr_link=addr_link, transactions=transactions)


if __name__ == "__main__":
    app.run()