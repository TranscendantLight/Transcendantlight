import uuid

class Admin:
    def __init__(self):
        self.valid_codes = {}  # code: amount

    def generate_deposit_code(self, amount):
        code = str(uuid.uuid4())
        self.valid_codes[code] = amount
        return code

    def is_valid_code(self, code):
        return code in self.valid_codes

    def get_code_amount(self, code):
        return self.valid_codes.pop(code, None)
