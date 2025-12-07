import os
import json
from datetime import datetime

TRANSACTIONS_FILE = "data/transactions.json"

class TransactionDB:
    @staticmethod
    def _initialize_file():
        default_data = {}
        os.makedirs(os.path.dirname(TRANSACTIONS_FILE), exist_ok=True)
        with open(TRANSACTIONS_FILE, 'w') as file:
            json.dump(default_data, file)
        return default_data

    @staticmethod
    def load():
        try:
            with open(TRANSACTIONS_FILE, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return TransactionDB._initialize_file()

    @staticmethod
    def save(data):
        with open(TRANSACTIONS_FILE, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def add_transaction(user_id, transaction_type, amount):
        data = TransactionDB.load()
        user_id = str(user_id)
        
        if user_id not in data:
            data[user_id] = []
            
        transaction_id = f"TXN{datetime.now().timestamp()}".replace(".", "")[:16]
        transaction = {
            "id": transaction_id,
            "type": transaction_type,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        data[user_id].insert(0, transaction)
        data[user_id] = data[user_id][:100]
        TransactionDB.save(data)
        return transaction_id
