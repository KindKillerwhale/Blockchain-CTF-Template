import os
import json
import time
from dataclasses import dataclass
from typing import Optional

import aiohttp
from flask import Flask, jsonify, request
from web3 import Web3
from web3.middleware import geth_poa_middleware

app = Flask(__name__)

rpc_url = os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:8545")

web3 = Web3(Web3.HTTPProvider(rpc_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# solc-select install VERSION
# solc-select use VERSION
# solc --bin --abi --optimize -o output YOUR_CONTRACT.sol
# The ABI JSON of Solidity uses false and true, but in Python, false and true are expressed as false and true. Therefore, you must change false to false and true to true when you import JSON into Python code.
contract_abi = [YOUR CONTRACT ABI]
contract_bytecode = 'YOUR CONTRACT BIN'


@dataclass
class RPCError:
    code: int
    message: str

PARSE_ERROR = RPCError(code=-32700, message="Parse error")
INVALID_REQUEST = RPCError(code=-32600, message="Invalid request")
METHOD_NOT_SUPPORTED = RPCError(code=-32004, message="Method not supported")
RESULT_UNAVAILABLE = RPCError(code=-32002, message="Resource unavailable")

ALLOWED_METHODS = frozenset(
    [
        "eth_blockNumber",
        "eth_call",
        "eth_chainId",
        "eth_estimateGas",
        "eth_gasPrice",
        "eth_getBalance",
        "eth_getBlockByHash",
        "eth_getBlockByNumber",
        "eth_getCode",
        "eth_getStorageAt",
        "eth_getTransactionByHash",
        "eth_getTransactionCount",
        "eth_getTransactionReceipt",
        "eth_sendRawTransaction",
        "net_version",
        "rpc_modules",
        "web3_clientVersion",
    ]
)

def error_response(error: RPCError, status_code: int, request_id: Optional[int] = None):
    return jsonify({
        "jsonrpc": "2.0",
        "error": {
            "code": error.code,
            "message": error.message,
        },
        "id": request_id,
    }), status_code

async def dispatch_request(provider: str, body: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(provider, json=body) as response:
            return await response.json()

user_data = {}

cnt = 0

def deploy_contract_for_user(user_id):
    global cnt

    while not os.path.exists("/shared/accounts.json"):
        time.sleep(1)

    with open("/shared/accounts.json") as f:
        accounts_data = json.load(f)
    
    ganache_accounts = accounts_data["addresses"]
    private_keys = accounts_data["private_keys"]
    # If you use 'ganache-cli', use the code below
    #ganache_accounts = list(accounts_data["addresses"].keys())
    #private_keys = [bytes(value['secretKey']['data']).hex() for value in accounts_data["addresses"].values()]

    if user_id not in user_data:
        deployer = list(ganache_accounts.keys())[cnt]
        private_key = private_keys[deployer]
        deployer = Web3.to_checksum_address(deployer)

        MirinaeStation = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        try:
            transaction = MirinaeStation.constructor(deployer).build_transaction({
                'from': deployer,
                'nonce': web3.eth.get_transaction_count(deployer),
                'gas': 2000000,
                'gasPrice': web3.to_wei('20', 'gwei')
            })

            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            rpc_url = f"RPC_URL/{user_id}"

            deployment_info = {
                "contractAddress": tx_receipt.contractAddress,
                "walletAddress": deployer,
                "privateKey": private_key,
                "rpcUrl": rpc_url,
            }

            user_data[user_id] = deployment_info
            cnt += 1

        except Exception as e:
            print(f"Error in transaction: {e}")
            return str(e), deployer, private_key

    return user_data[user_id]

@app.route('/info', methods=['GET'])
def info():
    user_id = request.remote_addr
    deployment_info = deploy_contract_for_user(user_id)
    return jsonify(deployment_info)

@app.route('/flag', methods=['GET'])
def flag():
    user_id = request.remote_addr
    deployment_info = deploy_contract_for_user(user_id)
    contract_address = deployment_info['contractAddress']
    wallet_address = deployment_info['walletAddress']

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    solved = contract.functions.isChallSolved().call({'from': wallet_address})

    result = "Challenge Solved!!" if solved else "Challenge Not Solved"
    with open(f'result_{user_id}.txt', 'w') as f:
        f.write(result)

    return result

@app.route('/interact/<user_id>', methods=['POST'])
async def interact(user_id):
    if user_id not in user_data:
        return error_response(RESULT_UNAVAILABLE, 400)

    try:
        body = request.get_json()
    except ValueError:
        return error_response(PARSE_ERROR, 415)

    request_id = body.get("id")
    body_keys = [key.lower() for key in body.keys()]
    if body_keys.count("method") != 1 or not isinstance(body["method"], str):
        return error_response(INVALID_REQUEST, 401, request_id)

    if body["method"] not in ALLOWED_METHODS:
        return error_response(METHOD_NOT_SUPPORTED, 401, request_id)

    try:
        if body["method"] == "eth_sendRawTransaction":
            raw_tx = body["params"][0]
            tx_hash = web3.eth.send_raw_transaction(raw_tx)
            response = {"jsonrpc": "2.0", "result": tx_hash.hex(), "id": request_id}
        else:
            #if body["method"] == "eth_call" or body["method"] == "eth_sendTransaction":
            #    if "gasPrice" not in body["params"][0]:
            #        body["params"][0]["gasPrice"] = web3.to_wei('20', 'gwei')
            response = await dispatch_request(
                os.getenv("WEB3_PROVIDER_URI", rpc_url), body
            )
            if (
                body["method"] in ("eth_getBlockByHash", "eth_getBlockByNumber")
                and "result" in response
            ):
                response["result"]["transactions"] = []
        return jsonify(response)
    except Exception as e:
        print(f"Exception: {e}")
        return error_response(RESULT_UNAVAILABLE, 500, request_id)

@app.route('/restart', methods=['GET'])
def restart():
    try:
        os.remove('deployment_info.json')
    except FileNotFoundError:
        pass
    user_data.clear()
    deployment_info = deploy_contract_for_user(request.remote_addr)
    return jsonify(deployment_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
