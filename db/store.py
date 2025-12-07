import json 
from db.guess import guessDB

stores = 'data/stores.json'

class StoreDB:

    @staticmethod
    def load():
        with open(stores,'r',encoding='utf-8') as file:
            return json.load(file)
        
    @staticmethod
    def save(data):
        with open(stores,'w',encoding='utf-8') as file:
            json.dump(data,file,indent=4)

    @staticmethod
    def exist(user_id):
        data = StoreDB.load()
        return str(user_id) in data
    
    @staticmethod
    def store_cr7(user_id):
        data = StoreDB.load()
        if str(user_id) not in data:
            data[str(user_id)] = StoreDB.get_teri_random_chars()
            StoreDB.save(data)
            return True
        return False

    @staticmethod
    def get_teri_random_chars():
        _kir17 = []
        _kir17.append(guessDB.get_random_character)
        _kir17.append(guessDB.get_random_character)
        _kir17.append(guessDB.get_random_character)
        return _kir17