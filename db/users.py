import json
import time
from db.harem import haremDB
from db.bank import banksDB

users = "data/users.json"


class userDB:


    @staticmethod
    def load():
        with open(users,'r',encoding="utf-8") as file:
            return json.load(file)
        
    @staticmethod
    def save(data):
        with open(users,'w',encoding="utf-8") as file:
            json.dump(data,file,indent=4)


    @staticmethod
    def exist_user(user_id):
        data = userDB.load()
        return str(user_id) in data 


    @staticmethod
    def create_user(user_id):
        data = userDB.load()
        user_id_str = str(user_id)
        if user_id_str not in data:
            data[user_id_str] = {
                "harem_id": haremDB.create_harem_id_for_user(),
                "bank_id": banksDB.create_bank(),
                "rubies": 0,
                "coins": 0,
                "wtokens": 0,
                "exp": 0,
                "level": 1,
                "premium": False,
                "cooldowns": {},
                "daily_reset": int(time.time()) + 86400
            }
            userDB.save(data)
            return True
        return False

    @staticmethod
    def remove_user(user_id):
        data = userDB.load()

        del data[user_id]
        userDB.save(data)


    @staticmethod
    def get_harem_id(user_id):
        data = userDB.load()

        if str(user_id) not in data:
            userDB.create_user(user_id)

        return data[str(user_id)]['harem_id']
    
    
    @staticmethod
    def get_bank_id(user_id,user_name):
        data = userDB.load()

        if str(user_id) not in data:
            userDB.create_user(user_id,user_name)
        return data[str(user_id)]['bank_id']
    
    @staticmethod
    def get_user_level(user_id):
        data = userDB.load()
        user_id = str(user_id)
        return data.get(user_id, {}).get('level', 1)

    @staticmethod
    def get_user_exp(user_id):
        data = userDB.load()
        user_id = str(user_id)
        return data.get(user_id, {}).get('exp', 0)

    @staticmethod
    def add_exp(user_id,exp):
        data = userDB.load()
        user_id = str(user_id)
        if user_id not in data:
            return False
        if 'exp' not in data[user_id]:
            data[user_id]['exp'] = 0
        if 'level' not in data[user_id]:
            data[user_id]['level'] = 1
        data[user_id]['exp'] += exp
        exp_needed = 1000 * (data[user_id]['level'] ** 2)
        if data[user_id]['exp'] >= exp_needed:
            data[user_id]['level'] += 1
            data[user_id]['exp'] -= exp_needed
            userDB.save(data)
            return {'level_up': True, 'new_level': data[user_id]['level']}
        userDB.save(data)
        return {'level_up': False}
    
    @staticmethod
    def is_premium(user_id):
        """Check if user has premium status"""
        data = userDB.load()
        user_id = str(user_id)
        return data.get(user_id, {}).get('premium', False)

    @staticmethod
    def set_premium(user_id, status=True):
        """Set premium status for user"""
        data = userDB.load()
        user_id = str(user_id)
        if user_id in data:
            data[user_id]['premium'] = status
            userDB.save(data)
            return True
        return False

    @staticmethod
    def get_discount(user_id):
        """Get user's purchase discount percentage"""
        return 10 if userDB.is_premium(user_id) else 0

    @staticmethod
    def get_cooldowns(user_id):
        """Get all user cooldowns"""
        data = userDB.load()
        user_id = str(user_id)
        return data.get(user_id, {}).get('cooldowns', {})

    @staticmethod
    def set_cooldown(user_id, cooldown_type, duration):
        """Set a cooldown for user"""
        data = userDB.load()
        user_id = str(user_id)
        if user_id not in data:
            return False
        
        if 'cooldowns' not in data[user_id]:
            data[user_id]['cooldowns'] = {}
        
        data[user_id]['cooldowns'][cooldown_type] = {
            'expires': int(time.time()) + duration
        }
        userDB.save(data)
        return True