import time

# Import the PyOTA library
import iota
from iota import Address
from iota import Transaction
from iota import TryteString
from iota.crypto.kerl import Kerl


# Import datetime libary
import time
import datetime

# Import json
import json

# Define full node to be used when uploading/downloading transaction records to/from the tangle
NodeURL = "https://nodes.thetangle.org:443"

# Create IOTA object
api=iota.Iota(NodeURL)

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

def example(seconds):
    print('Starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')

def threaded_task(duration):
    for i in range(duration):
        print("Working... {}/{}".format(i + 1, duration))
        time.sleep(1)

def get_transactions(barcode_ID):

    #barcode_ID = '1234567898765'

    # Get IOTA address from 13 digit barcode
    #address = CreateAddress(barcode_ID)

    address = [Address(b'TAAUUAKUZHKBWTCGKXTJGWHXEYJONN9MZZQUQLSZCLHFAWUWKHZCICTHISXBBAKGFQENMWMBOVWJTCMEWXKQDTJCV9')]

    # Find all transacions for selected IOTA address
    result = api.find_transactions(addresses=address)
        
    # Create a list of transaction hashes
    myhashes = result['hashes']

    # Print wait message
    print("Please wait while retrieving cleaning records from the tangle...")

    # Loop trough all transaction hashes
    for txn_hash in myhashes:
        
        # Convert to bytes
        txn_hash_as_bytes = bytes(txn_hash)

        # Get the raw transaction data (trytes) of transaction
        gt_result = api.get_trytes([txn_hash_as_bytes])
        
        # Convert to string
        trytes = str(gt_result['trytes'][0])
        
        # Get transaction object
        txn = Transaction.from_tryte_string(trytes)
        
        # Get transaction timestamp
        timestamp = txn.timestamp
        
        # Convert timestamp to datetime
        clean_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # Get transaction message as string
        txn_data = str(txn.signature_message_fragment.decode())
        
        # Convert to json
        json_data = json.loads(txn_data)
        
        # Check if json data has the expected json tag's
        if all(key in json.dumps(json_data) for key in ["tagID","hotel","room_number"]):
            # Add table row with json values
            # x.add_row([json_data['tagID'], json_data['hotel'], json_data['room_number'], clean_time])
            print('hei')

    # Sort table by cleaned datetime
    # x.sortby = "last_cleaned"

    # Return Dict
    #print(x)
