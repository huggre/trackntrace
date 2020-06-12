
import json

from iota_interact import send_transaction

seed = 'FYKVVGEI9AAZLLCFWYFFBG9SYRML9BENNGHYLQNMSXBRLXAERCPXOMQFBER9BDYIWMTYRSAIUZAEUZLUV'

# Address = PGGRIBEL9NGEXEMCJRTYZ9UOTWGZBJWUSAASLYVLTRVPEYEFJRSX9DY9KSWHXY9ZWRZGMNUM9DGNUTYXWNBVQRBXEZ

barcode_ID = '3234567898765'

# Create upload json
udata = {'barcode_ID' : '3234567898765', 'transaction_type' : 'Inbound', 'actor_name' : 'Bob the fisherman'}
msg = json.dumps(udata)

send_transaction(seed, barcode_ID, msg)

print('Done')
