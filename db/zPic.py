import json
from datetime import datetime

zpic = 'zPics.json'

class zPic:

    @staticmethod
    def load():
        with open(zpic,'r',encoding='utf-8') as file:
            return json.load(file)
        

    @staticmethod
    def save(data):
        with open(zpic,'w',encoding='utf-8') as file:
            json.dump(data,file,indent=4)


    @staticmethod
    def new_id(zpic_id):

        zpic_id = f"ZPIC{datetime.now().timestamp()}".replace(".", "")[:12]

        data = zPic.load()
        
        data['zpics'][zpic_id] = zpic_id

        zPic.save(data)

print(zPic.new_id(1212))

