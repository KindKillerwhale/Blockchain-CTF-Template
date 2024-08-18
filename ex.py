from web3 import Web3
import requests

info_response = requests.get('http://RPC_URL/info')
info_data = info_response.json()

user_id = info_data['user_id']

contract_info_response = requests.get(f'http://RPC_URL/info/{user_id}')
contract_info_data = contract_info_response.json()

contract_add = contract_info_data['contractAddress']
private_key = contract_info_data['privateKey']
rpc_url = contract_info_data['rpcUrl']
account_address = contract_info_data['walletAddress']

print("Contract Address:", contract_add)
print("Private Key:", private_key)
print("RPC URL:", rpc_url)
print("Account Address:", account_address)


web3 = Web3(Web3.HTTPProvider(rpc_url))
print("Are we connected?", web3.is_connected())

contract_abi = [YOUR CONTRACT ABI]
contract_add = "CONTRACT_ADDR"

example = web3.eth.contract(address=contract_add, abi=contract_abi)

gas_price = web3.to_wei('20', 'gwei')


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
