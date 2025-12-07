import json
import os

wtokens = "data/users.json"

class wtokensDB:
    @staticmethod
    def load():
        try:
            with open(wtokens, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Error decoding users.json, creating new file")
            return {}

    @staticmethod
    def save(data):
        try:
            os.makedirs('data', exist_ok=True)
            with open(wtokens, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving wtokens data: {str(e)}")

    @staticmethod
    def get_wtokens(user_id):
        try:
            data = wtokensDB.load()
            user_id = str(user_id)
            if user_id not in data:
                return 0
            return data[user_id].get('wtokens', 0)
        except Exception as e:
            print(f"Error getting wtokens for user {user_id}: {str(e)}")
            return 0

    @staticmethod
    def reduce_wtokens(user_id, amount):
        try:
            data = wtokensDB.load()
            user_id = str(user_id)
            current = data[user_id].get('wtokens', 0)
            data[user_id]['wtokens'] = max(0, current - amount)
            wtokensDB.save(data)
            return amount
        except Exception as e:
            print(f"Error reducing wtokens for user {user_id}: {str(e)}")
            return 0

    @staticmethod
    def enhance_wtokens(user_id, amount):
        try:
            data = wtokensDB.load()
            user_id = str(user_id)
            current = data[user_id].get('wtokens', 0)
            data[user_id]['wtokens'] = current + int(amount)
            wtokensDB.save(data)
            return amount
        except Exception as e:
            print(f"Error enhancing wtokens for user {user_id}: {str(e)}")
            return 0