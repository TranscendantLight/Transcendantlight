from datetime import datetime

class Wallet:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.transactions = [(datetime.now(), 'created', self.balance)]
        self.approved = False

    def deposit(self, amount):
        if amount <= 0:
            return False
        self.balance += amount
        self.transactions.append((datetime.now(), 'deposit', amount))
        return True

    def withdraw(self, amount):
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        self.transactions.append((datetime.now(), 'withdraw', amount))
        return True

    def transfer(self, amount, recipient_wallet):
        if amount <= 0 or amount > self.balance:
            return False
        self.withdraw(amount)
        recipient_wallet.deposit(amount)
        self.transactions.append((datetime.now(), f'transfer to {recipient_wallet.name}', amount))
        recipient_wallet.transactions.append((datetime.now(), f'received from {self.name}', amount))
        return True