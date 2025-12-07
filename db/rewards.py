import json
import os

rewards = "data/rewards.json"

class rewardsDB:
    @staticmethod
    def load():
        try:
            with open(rewards, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save(data):
        os.makedirs('data', exist_ok=True)
        with open(rewards, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def get_user_data(user_id):
        data = rewardsDB.load()
        return data.get(str(user_id), {})

    @staticmethod
    def update_user_data(user_id, reward_type, timestamp):
        data = rewardsDB.load()
        user_id = str(user_id)
        if user_id not in data:
            data[user_id] = {}
        data[user_id][reward_type] = timestamp
        rewardsDB.save(data)