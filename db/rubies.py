import json
from typing import Dict, Union

RUBIES_FILE = "data/users.json"

class EnhancedRubiesDB:
    @staticmethod
    def _load_data() -> Dict:
        try:
            with open(RUBIES_FILE, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _save_data(data: Dict) -> None:
        with open(RUBIES_FILE, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def get_rubies(user_id: Union[int, str]) -> int:
        data = EnhancedRubiesDB._load_data()
        user_id = str(user_id)
        return data.get(user_id, {}).get('rubies', 0)

    @staticmethod
    def update_rubies(user_id: Union[int, str], amount: int) -> None:
        data = EnhancedRubiesDB._load_data()
        user_id = str(user_id)
        
        if user_id not in data:
            data[user_id] = {'rubies': 0}
        
        data[user_id]['rubies'] += int(amount)
        EnhancedRubiesDB._save_data(data)
