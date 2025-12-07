import json
import os

games = "data/games.json"

class gamesDB:
    @staticmethod
    def _initialize_file():
        default_data = {
            "guess-games": {}
        }
        os.makedirs(os.path.dirname(games), exist_ok=True)
        with open(games, 'w', encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)
        return default_data

    @staticmethod
    def load():
        try:
            with open(games, 'r', encoding="utf-8") as file:
                data = json.load(file)
                # Ensure the guess-games key exists
                if 'guess-games' not in data:
                    data['guess-games'] = {}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return gamesDB._initialize_file()

    @staticmethod
    def save(data):
        with open(games, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def create_guess_game(guess_game_data, chat_id):
        data = gamesDB.load()
        data['guess-games'][str(chat_id)] = guess_game_data
        gamesDB.save(data)
        return True

    @staticmethod
    def remove_guess_game(chat_id):
        data = gamesDB.load()
        if str(chat_id) in data['guess-games']:
            del data['guess-games'][str(chat_id)]
            gamesDB.save(data)

    @staticmethod
    def check_exist_guess_game(chat_id):
        data = gamesDB.load()
        return str(chat_id) in data['guess-games']

    @staticmethod
    def get_guess_game(chat_id):
        data = gamesDB.load()
        return data['guess-games'].get(str(chat_id))

    @staticmethod
    def reload_guess_game_msg_charachter_id(chat_id, msg_character_id):
        data = gamesDB.load()
        if str(chat_id) in data['guess-games']:
            data['guess-games'][str(chat_id)]['msg'] = str(msg_character_id)
            gamesDB.save(data)

    @staticmethod
    def update_guess_game_status(chat_id, is_active):
        """Update the game active status"""
        data = gamesDB.load()
        if str(chat_id) in data['guess-games']:
            data['guess-games'][str(chat_id)]['is_active'] = is_active
            gamesDB.save(data)