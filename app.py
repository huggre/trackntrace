
# Import the PyOTA library
import iota
from iota import Address
from iota import Transaction
from iota import TryteString
from iota.crypto.kerl import Kerl

# Import redis and RQ
from redis import Redis
import rq
queue = rq.Queue('default', connection=Redis.from_url('redis://'))

# Import hashlib
import hashlib

# Import datetime libary
import time
import datetime

# Import json
import json

from random import randint
from time import strftime
from flask import Flask, render_template, flash, request
from wtforms import Form, SelectField, TextField, TextAreaField, validators, StringField, SubmitField

# Imports IotaGo form dependencies
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

# Import Flask-WTF
from flask_wtf import FlaskForm

# Import Flask Bootstrap
from flask_bootstrap import Bootstrap

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

# Create bootstrap object
bootstrap = Bootstrap(app)

# Define full node to be used when uploading/downloading transaction records to/from the tangle
# NodeURL = "https://nodes.thetangle.org:443"

# Create IOTA object
# api=iota.Iota(NodeURL)

class ReusableForm(FlaskForm):
    #actor_name = SelectField('Actor Name', choices=[('Hotel IOTA', 'Hotel IOTA'), ('Ben the Fisherman', 'Ben the Fisherman')])
    dropdown_list = ['Air', 'Land', 'Sea'] # You can get this from your model
    actor_name = SelectField('Actor Name', choices=dropdown_list, default=1)
    name = TextField('Name:', validators=[validators.required()])
    surname = TextField('Surname:', validators=[validators.required()])
    submit = SubmitField('Submit')

# Form for Register new transaction
class NewTransactionForm(FlaskForm):
    actor_name = SelectField('Actor Name', coerce=str)
    actor_key = StringField('Actor Key', validators=[DataRequired()])
    transaction_type = RadioField('Transaction Type', choices=[('1','Inbound'),('2','Outbound')], default=1, coerce=str)
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

# Function for generating IOTA addresse based on a given barcode ID
def CreateAddress(barcode_ID):
    barcode_tryte = TryteString.from_unicode(barcode_ID)
    astrits = TryteString(str(barcode_tryte).encode()).as_trits()
    checksum_trits = []
    sponge = Kerl()
    sponge.absorb(astrits)
    sponge.squeeze(checksum_trits)
    result = TryteString.from_trits(checksum_trits) 
    new_address = Address(result)
    return(new_address.with_valid_checksum())

# Function for hashing the transaction string
def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

# Function for publising a new transaction to the tangle
def publish_transaction(app, addr, msg):
    with app.app_context():
        # Define new IOTA transaction
        pt = iota.ProposedTransaction(address = iota.Address(addr), message = iota.TryteString.from_unicode(msg), tag = iota.Tag(b'HOTELIOTA'), value=0)

        # Print waiting message
        print("\nSending transaction...")

        FinalBundle = api.send_transfer(depth=3, transfers=[pt], min_weight_magnitude=14)['bundle']

        # Print confirmation message 
        print("\nTransaction sendt...")


@app.route("/", methods=['GET', 'POST'])
def index():

    form = ReusableForm(request.form)

    #print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        surname=request.form['surname']
        email=request.form['email']
        password=request.form['password']

        if form.validate():
            write_to_disk(name, surname, email)
            flash('Hello: {} {}'.format(name, surname))

        else:
            flash('Error: All Fields are Required')

    return render_template('index.html', form=form)


# Create new barcode
@app.route('/create_new_barcode', methods=['GET', 'POST'])
def create_new_barcode():

    form = TagForm()
    
    # Add tag types to SelectField
    form.tag_type.choices = [(tagtype_row.id, tagtype_row.name) for tagtype_row in tbl_tag_types.query.all()]

    # Add user accounts to SelectField
    #form.tag_account.choices = [(acc_row.id, acc_row.name) for acc_row in tbl_accounts.query.filter_by(owner=current_user.id)]

    if form.validate_on_submit():
        tag = tbl_tags()
        retval = save_tag(tag, form, new=True)
        if retval == True:
            flash('New tag created sucessfully!!')
            return redirect(url_for('tags'))
    return render_template('tag.html', title='New tag', form=form)

def send_async_email(app, msg):
    with app.app_context():
        time.sleep(5)
        print('HEI')
        #return True

def send_test():
    return True

# Register new transaction
@app.route('/register_new_transaction', methods=['GET', 'POST'])
def register_new_transaction():

    form = NewTransactionForm()
    
    # Add actor names to SelectField
    #form.actor_name.choices = ['Hotel IOTA Purchasing Dep.', 'Bob the fisherman', 'Trucks R Us',  'SeaTrans Inc.', 'WeDeliver Inc.', 'Hotel IOTA Warehouse']

    form.actor_name.choices = [('1', 'Hotel IOTA Purchasing Dep.'), ('2', 'Bob the fisherman'), ('3', 'Trucks R Us'), ('4', 'SeaTrans Inc.'), ('5', 'WeDeliver Inc.'), ('6', 'Hotel IOTA Warehouse')]
    
    if form.validate_on_submit():

        # Get values from form
        actor_name = form.actor_name.data
        actor_key = form.actor_key.data
        transaction_type = form.transaction_type.data
        barcode_ID = form.barcode.data

        #actor_name = 'ACTOR NAME'
        #actor_key = 'MYACTORKEY'
        #transaction_type = "Inbound"
        #barcode_ID = '1234567898765'

        # Create IOTA address from 13 digit barcode
        addr = CreateAddress(barcode_ID)
        
        # Build the string to be hashed
        hash_string = barcode_ID + actor_key + transaction_type
        
        # Hash the string
        transaction_hash = encrypt_string(hash_string)

        # Create upload json
        udata = {'Barcode ID' : barcode_ID, 'Transaction Type' : transaction_type, 'Actor Name' : actor_name, 'Transaction Hash' : transaction_hash}
        msg = json.dumps(udata)
        
        # add job to redis que
        job = queue.enqueue('pubtrans.publish_transaction', addr, msg)

        # Get the Redis job ID
        job_id = job.get_id()

        # Print the Redis job ID to terminal
        print(job_jid)

        # Show confirmation that new transaction was published
        flash('New transaction publised to address: ' + str(addr))

    return render_template('register_new_transaction.html', title='Register New Transaction', form=form)

# Display transaction history
@app.route('/display_transaction_history', methods=['GET', 'POST'])
def display_transaction_history():

    form = TagForm()
    
    # Add tag types to SelectField
    form.tag_type.choices = [(tagtype_row.id, tagtype_row.name) for tagtype_row in tbl_tag_types.query.all()]

    # Add user accounts to SelectField
    #form.tag_account.choices = [(acc_row.id, acc_row.name) for acc_row in tbl_accounts.query.filter_by(owner=current_user.id)]

    if form.validate_on_submit():
        tag = tbl_tags()
        retval = save_tag(tag, form, new=True)
        if retval == True:
            flash('New tag created sucessfully!!')
            return redirect(url_for('tags'))
    return render_template('tag.html', title='New tag', form=form)



if __name__ == "__main__":
    app.run()