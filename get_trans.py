from iota_interact import get_transactions

barcode_ID = '2234567898765'

msg_data = get_transactions(barcode_ID)

print(type(msg_data[0]))
print(msg_data)