import json
import os

banks = "data/banks.json"

class banksDB:
    
    @staticmethod
    def _initialize_file():
        """Initialize the banks.json file with default structure"""
        default_data = {
            "last-bank-id": 0,
            "banks": {}
        }
        os.makedirs(os.path.dirname(banks), exist_ok=True)
        with open(banks, 'w', encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)
        return default_data

    @staticmethod
    def load():
        try:
            with open(banks, 'r', encoding="utf-8") as file:
                data = json.load(file)
                if 'last-bank-id' not in data:
                    data['last-bank-id'] = 0
                if 'banks' not in data:
                    data['banks'] = {}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return banksDB._initialize_file()

    @staticmethod
    def save(data):
        with open(banks, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def new_bank_id():
        data = banksDB.load()
        data['last-bank-id'] += 1  # First increment the ID
        new_bank_id = data['last-bank-id']  # Then get the new value
        banksDB.save(data)  # Save the updated data
        return new_bank_id
    
    @staticmethod
    def bank_exists(bank_id):
        data = banksDB.load()
        return str(bank_id) in data['banks']

    @staticmethod
    def get_bank_balance_with_bank_id(bank_id):
        data = banksDB.load()
        bank_id = str(bank_id)
        if bank_id not in data['banks']:
            raise ValueError(f"Bank with ID {bank_id} does not exist")
        return data['banks'][bank_id]

    @staticmethod
    def withdraw_bank(bank_id, value):
        if not banksDB.bank_exists(bank_id):
            raise ValueError(f"Bank with ID {bank_id} does not exist")
            
        if value <= 0:
            raise ValueError("Withdrawal value must be positive")
            
        current_balance = banksDB.get_bank_balance_with_bank_id(bank_id)
        if current_balance < value:
            raise ValueError("Insufficient funds")
            
        new_balance = current_balance - value
        data = banksDB.load()
        data['banks'][str(bank_id)] = new_balance
        banksDB.save(data)
        return new_balance

    @staticmethod
    def save_bank(bank_id, value):
        if not banksDB.bank_exists(bank_id):
            raise ValueError(f"Bank with ID {bank_id} does not exist")
            
        if value <= 0:
            raise ValueError("Deposit value must be positive")
            
        current_balance = banksDB.get_bank_balance_with_bank_id(bank_id)
        new_balance = current_balance + value
        data = banksDB.load()
        data['banks'][str(bank_id)] = new_balance
        banksDB.save(data)
        return new_balance
    
    @staticmethod
    def create_bank():
        data = banksDB.load()
        bank_id = data['last-bank-id'] + 1
        data['last-bank-id'] = bank_id
        data['banks'][str(bank_id)] = 0
        banksDB.save(data)
        return bank_id
    