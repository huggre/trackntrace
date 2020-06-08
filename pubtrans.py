# Import the PyOTA library
import iota

# Define full node to be used when uploading/downloading transaction records to/from the tangle
NodeURL = "https://nodes.thetangle.org:443"

# Create IOTA object
api=iota.Iota(NodeURL)


# Function for publising a new transaction to the tangle
def publish_transaction(addr, msg):

    # Define new IOTA transaction
    pt = iota.ProposedTransaction(address = iota.Address(addr), message = iota.TryteString.from_unicode(msg), tag = iota.Tag(b'HOTELIOTA'), value=0)

    # Print waiting message
    print("\nSending transaction...")

    FinalBundle = api.send_transfer(depth=3, transfers=[pt], min_weight_magnitude=14)['bundle']

    # Print confirmation message 
    print("\nTransaction sendt...")