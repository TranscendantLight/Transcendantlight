import bcrypt
from datetime import datetime
class Wallet:
    def __init__(self, name, password):
        self.name = name
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.balance = 0
        self.approved = False
        self.locked = False
        self.transactions = [f"{datetime.now()}: Wallet '{name}' created"]

    def deposit(self, amount):
        if amount <= 0:
            return False
        self.balance += amount
        self.transactions.append(f"{datetime.now()}: Deposited {amount}")
        return True

    def transfer(self, to_wallet, amount):
        if not self.approved or not to_wallet.approved or amount > self.balance:
            return False
        self.balance -= amount
        to_wallet.balance += amount
        self.transactions.append(f"{datetime.now()}: Transferred {amount} to Wallet '{to_wallet.name}'")
        to_wallet.transactions.append(f"{datetime.now()}: Received {amount} from Wallet '{self.name}'")
        return True
