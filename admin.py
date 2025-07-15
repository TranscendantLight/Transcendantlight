import uuid

class Admin:
    def __init__(self):
        self.valid_codes = set()

    def approve_wallet(self, wallet):
        wallet.approved = True

    def generate_deposit_code(self):
        code = str(uuid.uuid4())
        self.valid_codes.add(code)
        return code

    def is_valid_code(self, code):
        if code in self.valid_codes:
            self.valid_codes.remove(code)
            return True
        return False