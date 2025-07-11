from web3 import Web3
import json

# Connect to Ethereum node (e.g., Infura)
infura_url = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check connection
print("Connected:", web3.isConnected())

# Replace with your contract address and ABI
contract_address = Web3.toChecksumAddress('0xYourContractAddress')
with open('contract_abi.json') as f:
    contract_abi = json.load(f)

# Load contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Choose the event to listen for
event_filter = contract.events.YourEvent.createFilter(fromBlock='latest')

# Listen for new events
print("Listening for events...")
while True:
    for event in event_filter.get_new_entries():
        print("New Event:", event)