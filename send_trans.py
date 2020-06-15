
import json

from iota_interact import send_transaction
from iota_interact import GenerateAddressFromBarcode

# Import datetime libary
import time
import datetime

seed = 'FYKVVGEI9AAZLLCFWYFFBG9SYRML9BENNGHYLQNMSXBRLXAERCPXOMQFBER9BDYIWMTYRSAIUZAEUZLUV'

# Address = PGGRIBEL9NGEXEMCJRTYZ9UOTWGZBJWUSAASLYVLTRVPEYEFJRSX9DY9KSWHXY9ZWRZGMNUM9DGNUTYXWNBVQRBXEZ

barcode_ID = '5234567898765'

addr =  GenerateAddressFromBarcode(barcode_ID)

# Get current time
timestamp = time.strftime("%Y-%m-%dT%H:%M")
actor_name = 'Bob the fisherman'
transaction_type = 'Inbound'

# Create upload json
udata = {'timestamp' : timestamp, 'actor_name' : actor_name, 'transaction_type' : transaction_type}
msg = json.dumps(udata)

send_transaction(seed, addr, msg)

print('Transactions sendt to: ' + str(addr))
