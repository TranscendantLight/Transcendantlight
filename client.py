from wallet import Wallet

# Dictionary to hold wallet objects
user_wallets = {}

def main():
    name = input("Enter your account name: ")

    if name not in user_wallets:
        print("Creating a new wallet...")
        wallet = Wallet(name)
        user_wallets[name] = wallet
    else:
        print("Welcome back!")
        wallet = user_wallets[name]

    while True:
        print(f"\n💼 Wallet: {wallet.name} | Balance: {wallet.balance}")
        print("1. Deposit\n2. Withdraw\n3. Transfer\n4. View Transactions\n5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            amt = int(input("Enter amount to deposit: "))
            wallet.deposit(amt)

        elif choice == "2":
            amt = int(input("Enter amount to withdraw: "))
            wallet.withdraw(amt)

        elif choice == "3":
            recipient_name = input("Enter recipient name: ")
            amt = int(input("Enter amount to transfer: "))
            if recipient_name not in user_wallets:
                user_wallets[recipient_name] = Wallet(recipient_name)
            recipient_wallet = user_wallets[recipient_name]
            wallet.transfer(amt, recipient_wallet)

        elif choice == "4":
            print("\n📜 Transactions:")
            for tx in wallet.transactions:
                print(tx)

        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()