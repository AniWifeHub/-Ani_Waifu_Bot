import json
import random
import os

characters = "data/characters.json"

class guessDB:
    
    @staticmethod
    def _initialize_file():
        default_data = {
            "last-id": 0,
            "characters": {}
        }
        os.makedirs(os.path.dirname(characters), exist_ok=True)
        with open(characters, 'w', encoding='utf-8') as file:
            json.dump(default_data, file, indent=4)
        return default_data

    @staticmethod
    def load():
        try:
            with open(characters, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if 'characters' not in data:
                    data['characters'] = {}
                if 'last-id' not in data:
                    data['last-id'] = 0
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return guessDB._initialize_file()

    @staticmethod
    def save(data):
        with open(characters, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def addWaifu(name, image, rarity, anime):
        data = guessDB.load()
        
        new_id = data['last-id'] + 1
        char_id = str(new_id)
        data['last-id'] = new_id
        if str(char_id) not in data['characters']:
            data["characters"][char_id] = {
                "id": char_id,
                "name": name,
                "image": image,
                "rarity": rarity,
                "anime": anime
            }
            guessDB.save(data)
            return char_id
        else:
            print(f"Fine ID: {char_id}")

    @staticmethod
    def removeWaifu(char_id):
        data = guessDB.load()
        char_id = str(char_id)
        
        if char_id in data['characters']:
            del data['characters'][char_id]
            guessDB.save(data)
            return True
        return False
    
    @staticmethod
    def listWaifus():
        data = guessDB.load()
        return list(data['characters'].items())
    
    @staticmethod
    def get_random_character():
        data = guessDB.load()
        if not data['characters']:
            return None
            
        char_id = random.choice(list(data['characters'].keys()))
        return data['characters'][char_id]
    
    @staticmethod
    def get_character_name_with_id(char_id):
        data = guessDB.load()
        char_id = str(char_id)
        return data['characters'].get(char_id)['name']
    
    @staticmethod
    def get_character_with_id(char_id):
        data = guessDB.load()
        char_id = str(char_id)
        return data['characters'].get(char_id)
    

    def is_duplicate_character(name: str, rarity: str) -> bool:
        data = guessDB.load()
        for char_data in data['characters'].values():
            if char_data['name'].lower() == name.lower() and char_data['rarity'] == rarity:
                return True
        return False
    
    @staticmethod
    def get_reward_with_rarity(rarity):
        data = guessDB.load()

        return data['rarity_rewards'][rarity]
    

    @staticmethod
    def add_rarity_reward(rarity, reward):
        data = guessDB.load()
        
        if 'rarity_rewards' not in data:
            data['rarity_rewards'] = {}
        
        if rarity in data['rarity_rewards']:
            return False
            
        data['rarity_rewards'][rarity] = reward
        guessDB.save(data)
        return True

    @staticmethod
    def change_rarity_reward(rarity, new_reward):
        data = guessDB.load()
        
        if 'rarity_rewards' not in data or rarity not in data['rarity_rewards']:
            return False
            
        data['rarity_rewards'][rarity] = new_reward
        guessDB.save(data)
        return True

    @staticmethod
    def rarity_rewards():
        data = guessDB.load()
        return list(data.get('rarity_rewards', {}).items())
    
    
    @staticmethod
    def add_rarity_sticker(rarity, sticker):
        data = guessDB.load()

        if 'rarity_stickers' not in data:
            data['rarity_stickers'] = {}

        if rarity in data['rarity_stickers']:
            return False

        data['rarity_stickers'][rarity] = sticker
        guessDB.save(data)
        return True

    @staticmethod
    def change_rarity_sticker(rarity, new_sticker):
        data = guessDB.load()

        if 'rarity_stickers' not in data or rarity not in data['rarity_stickers']:
            return False

        data['rarity_stickers'][rarity] = new_sticker
        guessDB.save(data)
        return True

    @staticmethod
    def rarity_stickers():
        data = guessDB.load()
        return list(data.get('rarity_stickers', {}).items())
    
    @staticmethod
    def get_rarity_sticker(rarity):
        data = guessDB.load()
        return data.get('rarity_stickers', {}).get(rarity, None)
    
    @staticmethod
    def get_last_id():
        data = guessDB.load()
        return data.get('last-id', 0)
    
    @staticmethod
    def get_character_id_with_name(name):
        name = str(name).lower()
        data = guessDB.load()
    
        if "characters" not in data:
            return None
        
        for char_id, character in data["characters"].items():
            if name in character["name"].lower():
                return character        