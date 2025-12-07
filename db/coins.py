import json

coins = "data/users.json"

class coinsDB:


    @staticmethod
    def load():
        with open(coins,'r',encoding="utf-8") as file:
            return json.load(file)


    @staticmethod
    def save(data):
        with open(coins,'w',encoding="utf-8") as file:
            json.dump(data,file,indent=4)

    @staticmethod
    def get_coins(user_id):
        data = coinsDB.load()
        return data[str(user_id)]['coins']
    
    @staticmethod
    def enhance_coins(user_id,amount):
        data = coinsDB.load()
        user_coins = coinsDB.get_coins(str(user_id))
        data[str(user_id)]['coins'] = int(user_coins) + int(amount)
        coinsDB.save(data)

    @staticmethod
    def reduce_coins(user_id,amount):
        data = coinsDB.load()
        user_coins = coinsDB.get_coins(str(user_id))
        data[str(user_id)]['coins'] = user_coins - amount
        coinsDB.save(data)