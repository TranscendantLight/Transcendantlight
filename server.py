from flask import Flask, request, jsonify
from wallet import Wallet
from admin import Admin

app = Flask(__name__)
wallets = {}
admin = Admin()

@app.route("/create_wallet", methods=["POST"])
def create_wallet():
    name = request.json.get("name")
    if name in wallets:
        return jsonify({"message": "Wallet already exists."}), 400
    wallet = Wallet(name)
    wallets[name] = wallet
    return jsonify({"message": "Wallet created. Awaiting approval."})

@app.route("/approve_wallet", methods=["POST"])
def approve_wallet():
    name = request.json.get("name")
    wallet = wallets.get(name)
    if wallet:
        admin.approve_wallet(wallet)
        return jsonify({"message": f"Wallet for '{name}' approved."})
    return jsonify({"error": "Wallet not found."}), 404

@app.route("/generate_deposit_code", methods=["POST"])
def generate_deposit_code():
    code = admin.generate_deposit_code()
    return jsonify({"code": code})

@app.route("/deposit", methods=["POST"])
def deposit():
    name = request.json.get("name")         # Get wallet name from request
    amount = request.json.get("amount")     # Get amount to deposit
    code = request.json.get("code")         # Get deposit code

    wallet = wallets.get(name)              # Look up the wallet by name

    # 🔐 Only allow deposit if wallet is approved AND code is valid
    if wallet and wallet.approved and admin.is_valid_code(code):
        success = wallet.deposit(amount)
        if success:
            return jsonify({"message": f"{amount} deposited to {name}."})
        else:
            return jsonify({"error": "Invalid deposit amount."}), 400
    # 🚫 If wallet isn't approved or code fails validation, reject
    return jsonify({"error": "Wallet not approved or code invalid."}), 400

@app.route("/wallet_info", methods=["GET"])
def wallet_info():
    name = request.args.get("name")
    wallet = wallets.get(name)
    if wallet:
        return jsonify({
            "name": wallet.name,
            "balance": wallet.balance,
            "approved": wallet.approved,
            "transactions": wallet.transactions
        })
    return jsonify({"error": "Wallet not found."}), 404
