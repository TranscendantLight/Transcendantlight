import requests

BASE_URL = "http://127.0.0.1:5000"

def approve_wallet():
    name = input("Wallet name to approve: ")
    res = requests.post(f"{BASE_URL}/approve_wallet", json={"name": name})
    print(res.json())

def generate_code():
    res = requests.post(f"{BASE_URL}/generate_deposit_code")
    print(f"🪙 Deposit Code: {res.json().get('code')}")

def view_wallet():
    name = input("Wallet name to inspect: ")
    res = requests.get(f"{BASE_URL}/wallet_info", params={"name": name})
    data = res.json()
    if "error" in data:
        print(data["error"])
    else:
        print(f"\n👁️ Admin View — Wallet: {data['name']}")
        print(f"Balance: {data['balance']}")
        print(f"Approved: {data['approved']}")
        print("📜 Transactions:")
        for tx in data["transactions"]:
            print(tx)

def main():
    print("🔐 TranscendantLight Admin CLI")
    while True:
        print("\n1. Approve Wallet\n2. Generate Deposit Code\n3. View Wallet Info\n4. Exit")
        choice = input("Select: ")
        if choice == "1": approve_wallet()
        elif choice == "2": generate_code()
        elif choice == "3": view_wallet()
        elif choice == "4":
            print("🔒 Exiting Admin Interface.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()