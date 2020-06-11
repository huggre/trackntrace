
import json

from iota_interact import send_transaction

seed = 'FYKVVGEI9AAZLLCFWYFFBG9SYRML9BENNGHYLQNMSXBRLXAERCPXOMQFBER9BDYIWMTYRSAIUZAEUZLUV'

# Address = PGGRIBEL9NGEXEMCJRTYZ9UOTWGZBJWUSAASLYVLTRVPEYEFJRSX9DY9KSWHXY9ZWRZGMNUM9DGNUTYXWNBVQRBXEZ

barcode_ID = '2234567898765'

# Create upload json
udata = {'Barcode ID' : '1234567898765', 'Transaction Type' : 'Inbound', 'Actor Name' : 'Bob the fisherman'}
msg = json.dumps(udata)

send_transaction(seed, barcode_ID, msg)

print('Done')
