import openai
from web3 import Web3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the environment variables
infura_url = os.getenv("INFURA_URL")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Connect to an Ethereum node using Infura or any provider
web3 = Web3(Web3.HTTPProvider(infura_url))

# Set the OpenAI API key
openai.api_key = openai_api_key

# Blockchain functions
def get_balance(address: str):
    """Get balance of an Ethereum address."""
    balance_wei = web3.eth.get_balance(address)
    return web3.fromWei(balance_wei, 'ether')

def get_contract_data(address: str):
    """Fetch basic contract information from an Ethereum address."""
    contract = web3.eth.contract(address=web3.toChecksumAddress(address), abi=[])
    # Example: retrieve the name of the token if ERC-20
    try:
        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()
        return {"name": name, "symbol": symbol, "decimals": decimals}
    except:
        return {"error": "Contract is not ERC-20 or doesn't follow standard conventions"}

def generate_erc20_token(name: str, symbol: str, initial_supply: int):
    """Generate ERC-20 token smart contract."""
    erc20_abi = '''
    [
        {
            "inputs": [],
            "stateMutability": "nonpayable",
            "type": "constructor",
            "name": "constructor",
            "args": []
        },
        {
            "name": "name",
            "outputs": [{"type": "string"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "name": "symbol",
            "outputs": [{"type": "string"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    '''
    # Here, the contract code for ERC-20 needs to be written or fetched for deployment
    return f"ERC-20 Token {name} ({symbol}) with initial supply {initial_supply} created."

def explain_blockchain_concept(concept: str):
    """Provide an explanation for a blockchain concept using OpenAI GPT."""
    prompt = f"Explain the concept of {concept} in blockchain technology."
    response = openai.Completion.create(
        engine="text-davinci-003", 
        prompt=prompt, 
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Flask route for assistant API
@app.route("/token-gpt", methods=["POST"])
def token_gpt():
    data = request.json
    action = data.get("action")
    
    if action == "get_balance":
        address = data.get("address")
        if not web3.isAddress(address):
            return jsonify({"error": "Invalid Ethereum address"})
        balance = get_balance(address)
        return jsonify({"balance": balance})
    
    elif action == "get_contract_data":
        address = data.get("address")
        if not web3.isAddress(address):
            return jsonify({"error": "Invalid contract address"})
        contract_data = get_contract_data(address)
        return jsonify(contract_data)
    
    elif action == "generate_erc20":
        name = data.get("name")
        symbol = data.get("symbol")
        initial_supply = data.get("initial_supply")
        result = generate_erc20_token(name, symbol, initial_supply)
        return jsonify({"message": result})
    
    elif action == "explain_concept":
        concept = data.get("concept")
        explanation = explain_blockchain_concept(concept)
        return jsonify({"explanation": explanation})
    
    else:
        return jsonify({"error": "Unknown action"})

if __name__ == "__main__":
    app.run(debug=True)
