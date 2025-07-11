from web3 import Web3

# Connect to Ethereum node (e.g., Infura or local)
infura_url = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
web3 = Web3(Web3.HTTPProvider(infura_url))

# Your wallet credentials
sender_address = '0xYourAddress'
private_key = '0xYourPrivateKey'  # NEVER expose this in real code

# Recipient address
receiver_address = '0xReceiverAddress'

# Build transaction
nonce = web3.eth.get_transaction_count(sender_address)
tx = {
    'nonce': nonce,
    'to': receiver_address,
    'value': web3.to_wei(0.01, 'ether'),  # Amount in ETH
    'gas': 21000,
    'gasPrice': web3.to_wei('50', 'gwei'),
    'chainId': 1  # 1 = mainnet, 5 = Goerli, 11155111 = Sepolia
}

# Sign transaction
signed_tx = web3.eth.account.sign_transaction(tx, private_key)

# Send transaction
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

# Get transaction hash
print(f"Transaction sent! Hash: {web3.to_hex(tx_hash)}")