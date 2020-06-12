

# Import Iota interact functions
from iota_interact import send_transaction
from iota_interact import get_transactions
from iota_interact import GenerateAddressFromBarcode

# Import the PyOTA library
#import iota
#from iota import Address
#from iota import Transaction
#from iota import TryteString
#from iota.crypto.kerl import Kerl

# Import redis and RQ
from redis import Redis
import rq
queue = rq.Queue('default', connection=Redis.from_url('redis://'))

# Import flask table
from flask_table import Table, Col

# Import hashlib
import hashlib

# Import datetime libary
import time
import datetime

# Import json
import json

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
NodeURL = "https://nodes.thetangle.org:443"

# Create IOTA object
#api=iota.Iota(NodeURL)

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    description = Col('Description')

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

# Create bootstrap object
bootstrap = Bootstrap(app)

#loop2 = asyncio.get_event_loop()

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
    actor_seed = StringField('Actor Seed', validators=[DataRequired()])
    transaction_type = RadioField('Transaction Type', choices=[('1','Inbound'),('2','Outbound')], default=1, coerce=str)
    barcode = StringField('Barcode', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Form for displaying transaction history
class DisplayTransactionHistoryForm(FlaskForm):
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


# Register transaction
@app.route('/register_transaction', methods=['GET', 'POST'])
def register_transaction():

    form = RegisterTransactionForm()
    
    form.actor_name.choices = [('1', 'Hotel IOTA Purchasing Dep.'), ('2', 'Bob the fisherman'), ('3', 'Trucks R Us'), ('4', 'SeaTrans Inc.'), ('5', 'WeDeliver Inc.'), ('6', 'Hotel IOTA Warehouse')]
    
    if form.validate_on_submit():
        
        # Get values from form
        actor_name = dict(form.actor_name.choices).get(form.actor_name.data)
        actor_seed = form.actor_seed.data
        transaction_type = dict(form.transaction_type.choices).get(form.transaction_type.data)
        barcode_ID = form.barcode.data

        # Create IOTA address from 13 digit barcode
        addr = GenerateAddressFromBarcode(barcode_ID)
        
        # Create upload json
        udata = {'Barcode ID' : barcode_ID, 'Transaction Type' : transaction_type, 'Actor Name' : actor_name}
        msg = json.dumps(udata)
        
        # add job to redis que
        job = queue.enqueue('send_transaction', actor_seed, addr, msg)

        # Get the redis job ID
        job_id = job.get_id()

        # Print the redis job ID to terminal
        print("New redis job added to que" + job_id)

        # Show confirmation that new transaction was published
        flash('New transaction registered to address: ' + str(addr))

    return render_template('register_transaction.html', title='Register transaction', form=form)

# Display transaction history form
@app.route('/display_transaction_history', methods=['GET', 'POST'])
def display_transaction_history():

    form = DisplayTransactionHistoryForm()

    if form.validate_on_submit():

        # Get barcode ID from form
        barcode_ID = form.barcode.data
        
        # Get transaction data from IOTA tangle
        #get_transaction_data_from_tangle(barcode_ID)

        # loop = asyncio.get_event_loop()
        #loop = asyncio.new_event_loop()
        # loop2.run_until_complete(get_transactions(barcode_ID))

        transactions = get_transactions(barcode_ID)

        #msg_data = 'test'

        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(get_transactions(barcode_ID))


        #t = AppContextThread(target=get_transaction_data_from_tangle)
        #t.start()
        #t.join()

        #print('Done')
        #duration=10
        #thread = Thread(target=threaded_task, args=(duration,))
        #thread.daemon = True
        #thread.start()

        #threaded_task(duration)

        #loop.run_until_complete(get_transaction_data_from_tangle(barcode_ID))

        #return redirect(url_for('display_transaction_history_result'))
        return display_transaction_history_result(transactions)
    return render_template('display_transaction_history.html', title='Display transaction history', form=form)


# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

# Display transaction history result
@app.route('/display_transaction_history_result')
def display_transaction_history_result(transactions):

    items = [Item('Name1', 'Description1'),
            Item('Name2', 'Description2'),
            Item('Name3', 'Description3')]

    # Populate the table
    #table = ItemTable(items)

    #return render_template('display_transaction_history_result.html', title='Transaction history', items=items)
    return render_template('test.html', title='Transaction history', transactions=transactions)


if __name__ == "__main__":
    app.run()