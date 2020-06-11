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


# Function for generating IOTA address from a given barcode ID
def GenerateAddressFromBarcode(barcode_ID):
    barcode_tryte = TryteString.from_unicode(barcode_ID)
    astrits = TryteString(str(barcode_tryte).encode()).as_trits()
    checksum_trits = []
    sponge = Kerl()
    sponge.absorb(astrits)
    sponge.squeeze(checksum_trits)
    result = TryteString.from_trits(checksum_trits) 
    new_address = Address(result)
    return(new_address.with_valid_checksum())

def send_transaction(seed, addr, msg):

    # Create IOTA object
    api=iota.Iota(NodeURL, seed=seed)

    # Define new IOTA transaction
    pt = iota.ProposedTransaction(address = iota.Address(addr), message = iota.TryteString.from_unicode(msg), tag = iota.Tag(b'HOTELIOTA'), value=0)

    # Print waiting message
    print("\nSending transaction...")

    FinalBundle = api.send_transfer(depth=3, transfers=[pt], min_weight_magnitude=14)['bundle']

    # Print confirmation message 
    print("\nTransaction sendt...")



def get_transactions(barcode_ID):

    # Create IOTA object
    api=iota.Iota(NodeURL)

    # Generate IOTA address from barcode
    addr = GenerateAddressFromBarcode(barcode_ID)

    # Find all transacions for selected IOTA address
    result = api.find_transactions(addresses=[addr,])
        
    # Create a list of transaction hashes
    myhashes = result['hashes']

    # Print wait message
    print("Please wait while retrieving cleaning records from the tangle...")


    msg_data = []

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
        if all(key in json.dumps(json_data) for key in ["Barcode ID","Transaction Type","Actor Name"]):
            # Append meassage fragment data to dict
            msg_data.append(txn_data)

    return msg_data
