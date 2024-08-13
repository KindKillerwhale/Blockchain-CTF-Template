from web3 import Web3

account_address = 'ACCOUNT_ADDRESS'
private_key = 'PRIVATE_KEY'
rpc_url = 'RPC_URL'
web3 = Web3(Web3.HTTPProvider(rpc_url))
print("Are we connected?", web3.isConnected())

contract_abi = [YOUR CONTRACT ABI]
contract_add = "CONTRACT_ADDR"

example = web3.eth.contract(address=contract_add, abi=contract_abi)

gas_price = web3.toWei('20', 'gwei')


# Specify 'gasPrice' because it should follow the 'legacy' format.
nonce = web3.eth.get_transaction_count(account_address)
transaction = example.functions.CONTRACT_FUNCTION(ARG).buildTransaction({
    'from': account_address,
    'nonce': nonce,
    'chainId': web3.eth.chain_id,
    'gas': 2000000,
    'gasPrice': gas_price
})
signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)