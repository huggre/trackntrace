from iota_interact import get_transactions

barcode_ID = '5234567898765'

transactions = get_transactions(barcode_ID)

print(transactions)
