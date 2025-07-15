import requests

BASE_URL = "http://127.0.0.1:5000"

def create_wallet():
    name = input("Enter your wallet name: ")
    res = requests.post(f"{BASE_URL}/create_wallet", json={"name": name})
    print(res.json())

def deposit():
    name = input("Your wallet name: ")
    amount = int(input("Amount to deposit: "))
    code = input("Enter deposit code: ")
    res = requests.post(f"{BASE_URL}/deposit", json={
        "name": name,
        "amount": amount,
        "code": code
    })
    print(res.json())

def wallet_info():
    name = input("Enter wallet name to view: ")
    res = requests.get(f"{BASE_URL}/wallet_info", params={"name": name})
    data = res.json()
    if "error" in data:
        print(data["error"])
    else:
        print(f"\n🔮 Wallet: {data['name']}")
        print(f"Balance: {data['balance']}")
        print(f"Approved: {data['approved']}")
        print("📜 Transactions:")
        for tx in data["transactions"]:
            print(tx)

def transfer():
    sender = input("Your wallet name: ")
    receiver = input("Recipient's wallet name: ")
    amount = int(input("Amount to transfer: "))

    # Transfer works locally, so we simulate by calling deposit on receiver
    # This assumes both wallets already exist and are approved
    # You would need to add a /transfer endpoint to do this properly via server

    print("\n⚠️ Transfers require server-side support.")
    print("To implement real transfers, ask your admin to add a /transfer endpoint!")

def main():
    print("✨ Welcome to TranscendantLight ✨")
    while True:
        print("\n1. Create Wallet\n2. Deposit\n3. View Wallet Info\n4. Transfer (placeholder)\n5. Exit")
        choice = input("Choose: ")
        if choice == "1": create_wallet()
        elif choice == "2": deposit()
        elif choice == "3": wallet_info()
        elif choice == "4": transfer()
        elif choice == "5": break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()