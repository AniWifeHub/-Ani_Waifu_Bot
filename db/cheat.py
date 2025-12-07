import json

cheat_file = 'data/cheat.json'

class CheatDB:

    @staticmethod
    def load():
        with open(cheat_file, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    @staticmethod
    def save(data):
        with open(cheat_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def check_bypass(user_id):
        data = CheatDB.load()
        return str(user_id) in data.get('bypass', {})
    
    @staticmethod
    def add_bypass(user_id):
        data = CheatDB.load()
        if str(user_id) not in data['bypass']:
            data['bypass'][str(user_id)] = True
            CheatDB.save(data)
    
    @staticmethod
    def remove_bypass(user_id):
        data = CheatDB.load()
        if str(user_id) in data['bypass']:
            del data['bypass'][str(user_id)]
            CheatDB.save(data)

    @staticmethod
    def get_bypass_list():
        data = CheatDB.load()
        return data['bypass']
    
    @staticmethod
    def clear_bypass():
        data = CheatDB.load()
        data['bypass'] = {}
        CheatDB.save(data)