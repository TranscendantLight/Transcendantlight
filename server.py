from flask import Flask, request, jsonify
import bcrypt, requests, time, threading, os
from wallet import Wallet
from admin import Admin
from colours import Red, Green

app = Flask(__name__, static_folder='web', static_url_path='/web')
wallets = {}
admin = Admin()
hashed_admin_password = os.environ.get('hashed_admin_password').encode()

def ping():
    while True:
        try:
            requests.get("https://transcendantlight.onrender.com/health")
        except:
            pass
        time.sleep(600)

threading.Thread(target=ping, daemon=True).start()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online"})

@app.route('/admin_approve', methods=["POST"])
def admin_approve():
    password = request.json.get("password")
    if bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({'approved' : 'True'})
    return jsonify({'approved': 'False'}), 403

@app.route("/create_wallet", methods=["POST"])
def create_wallet():
    name = request.json.get("name")
    password = request.json.get("password")
    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400
    if name in wallets:
        return jsonify({"error": "Wallet already exists"}), 400
    wallets[name] = Wallet(name, password)
    return jsonify({"message": f"Wallet '{name}' created. Waiting for admin approval."})

@app.route("/approve_wallet", methods=["POST"])
def approve_wallet():
    name = request.json.get("name")
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    wallet = wallets.get(name)
    if wallets and wallet:
        if wallet.approved:
            return jsonify({"error": "Wallet already approved"}), 400
        wallet.approved = True
        return jsonify({"message": f"Wallet '{name}' approved."})
    return jsonify({"error": "Wallet not found."}), 404
        
@app.route("/generate_deposit_code", methods=["POST"])
def generate_deposit_code():
    amount = request.json.get("amount")
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    code = admin.generate_deposit_code(amount)
    return jsonify({"code": code, "amount": amount})

@app.route("/destroy_all_codes", methods=["POST"])
def destroy_all_codes():
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    admin.valid_codes = {}
    return jsonify({"message": "All deposit codes destroyed."})

@app.route('/view_all_codes', methods=["POST"])
def view_all_codes():
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    if not admin.valid_codes:
        return jsonify({"error": "No valid deposit codes"}), 404
    return jsonify(admin.valid_codes)

@app.route("/deposit", methods=["POST"])
def deposit():
    name = request.json.get("name")
    code = request.json.get("code")
    password = request.json.get("password")
    wallet = wallets.get(name)
    
    if wallet.locked:
        return jsonify({"error": "Wallet is locked. Contact an administrator for more details"}), 403
    
    if not bcrypt.checkpw(password.encode(), wallet.password):
        return jsonify({"error": "Invalid password. Contact an administartor to reset your password."}), 403
    
    if wallet and wallet.approved and admin.is_valid_code(code):
        amount = admin.get_code_amount(code)
        if amount is not None and wallet.deposit(amount):
            return jsonify({"message": f"{amount} deposited to {name}."})
        return jsonify({"error": "Deposit failed"}), 400
    elif not wallet.approved:
        return jsonify({"error": "Wallet not approved"}), 403
    elif not admin.is_valid_code(code):
        return jsonify({"error": "Invalid deposit code"}), 400
    elif not wallet:
        if not admin.is_valid_code(code):
            return jsonify({"error": "Wallet not found and invalid deposit code"}), 400
        return jsonify({"error": "Wallet not found"}), 404

@app.route("/wallet_info", methods=["POST"])
def wallet_info():
    name = request.json.get("name")
    password = request.json.get("password")
    wallet = wallets.get(name)
    if not bcrypt.checkpw(password.encode(), wallet.password):
        return jsonify({"error": "Invalid password. Contact an administartor to reset your password."}), 403
    if wallet:
        return jsonify({
            "name": wallet.name,
            "balance": wallet.balance,
            "approved": (Green(wallet.approved) if wallet.approved 
                         else Red(wallet.approved)),
            "locked": (Red(wallet.locked) if wallet.locked 
                       else Green(wallet.locked)),
            "transactions": wallet.transactions
        })
    return jsonify({"error": "Wallet not found"}), 404

@app.route("/admin_wallet_info", methods=["POST"])
def admin_wallet_info():
    name = request.json.get("name")
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    wallet = wallets.get(name)
    if wallet:
        return jsonify({
            "name": wallet.name,
            "balance": wallet.balance,
            "approved": (Green(wallet.approved) if wallet.approved 
                         else Red(wallet.approved)),
            "locked": (Red(wallet.locked) if wallet.locked 
                       else Green(wallet.locked)),
            "transactions": wallet.transactions
        })
    return jsonify({"error": "Wallet not found"}), 404

@app.route("/all_wallet_info", methods=["POST"])
def all_wallet_info(): 
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403     
    if wallets:
        return jsonify([{
            "name": wallet.name,
            "balance": wallet.balance,
            "approved": (Green(wallet.approved) if wallet.approved 
                         else Red(wallet.approved)),
            "locked": (Red(wallet.locked) if wallet.locked 
                       else Green(wallet.locked)),
            "transactions": wallet.transactions
        } for wallet in wallets.values()])
    return jsonify({"error": "No wallets"}), 404

@app.route("/destroy_wallet", methods = ["POST"])
def destroy_wallet():
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    name = request.json.get("name")
    if name in wallets:
        del wallets[name]
        return jsonify({"message": f"Wallet '{name}' destroyed."})
    return jsonify({"error": "Wallet not found"}), 404

@app.route("/destroy_all_wallets", methods=["POST"])
def destroy_all_wallets():
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    if wallets:
        wallets.clear()
        return jsonify({"message": "All wallets destroyed."})
    return jsonify({"error": "No wallets to destroy"}), 404

@app.route("/lock_wallet", methods=["POST"])
def lock_wallet():
    name = request.json.get("name")
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    wallet = wallets.get(name)
    if wallet:
        wallet.locked = True
        return jsonify({"message": f"Wallet '{name}' locked."})
    return jsonify({"error": "Wallet not found"}), 404

@app.route("/unlock_wallet", methods=["POST"])
def unlock_wallet():
    name = request.json.get("name")
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    wallet = wallets.get(name)
    if wallet:
        wallet.locked = False
        return jsonify({"message": f"Wallet '{name}' unlocked."})
    return jsonify({"error": "Wallet not found"}), 404

@app.route("/reset_server", methods=["POST"])
def reset_server():
    password = request.json.get("password")
    if not bcrypt.checkpw(password.encode(), hashed_admin_password):
        return jsonify({"error": "Invalid admin password"}), 403
    if wallets and admin.valid_codes:
        wallets.clear()
        admin.valid_codes.clear()
        return jsonify({"message": "Server reset successfully."})
    elif not wallets and admin.valid_codes:
        admin.valid_codes.clear()
        return jsonify({"message": "Deposit codes cleared, no wallets to reset."})
    elif wallets and not admin.valid_codes:
        wallets.clear()
        return jsonify({"message": "Wallets cleared, no deposit codes to reset."})
    return jsonify({"error": "No wallets or codes to reset"}), 404

@app.route("/transfer", methods=["POST"])
def transfer():
    sender_name = request.json.get("sender")
    sender_password = request.json.get("password")
    if not bcrypt.checkpw(sender_password.encode(), wallets[sender_name].password):
        return jsonify({"error": "Invalid password. Contact an administartor to reset your password."}), 403
    receiver_name = request.json.get("receiver")
    amount = request.json.get("amount")

    sender = wallets.get(sender_name)
    receiver = wallets.get(receiver_name)

    if sender.locked or receiver.locked:
        return jsonify({"error": "One or both wallets is locked. Contact an administrator for more details"}), 403
    
    if not sender or not receiver:
        return jsonify({"error": "One or both wallets not found"}), 404
    if not sender.approved or not receiver.approved:
        return jsonify({"error": "Both wallets must be approved"}), 400
    if not isinstance(amount, int) or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if sender.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    if sender.transfer(receiver, amount):
        return jsonify({"message": f"{amount} transferred from {sender_name} to {receiver_name}."})
    return jsonify({"error": "Transfer failed"}), 400
