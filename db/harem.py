import json
import logging

logger = logging.getLogger(__name__)

harems = "data/harems.json"

class haremDB:
    @staticmethod
    def load():
        try:
            with open(harems, 'r', encoding="utf-8") as file:
                data = json.load(file)
                if 'last-id' not in data:
                    data['last-id'] = 0
                if 'harems' not in data:
                    data['harems'] = {}
                return data
        except FileNotFoundError:
            logger.warning(f"{harems} not found, creating new one")
            return {"last-id": 0, "harems": {}}
        except Exception as e:
            logger.error(f"Error loading {harems}: {e}")
            return {"last-id": 0, "harems": {}}

    @staticmethod
    def save(data):
        try:
            with open(harems, 'w', encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logger.error(f"Error saving {harems}: {e}")

    @staticmethod
    def create_new_harem_id():
        data = haremDB.load()
        last_id = data.get('last-id', 0)
        new_last_id = int(last_id) + 1
        data['last-id'] = new_last_id
        haremDB.save(data)
        return new_last_id

    @staticmethod
    def create_harem_id_for_user():
        data = haremDB.load()
        last_id = data.get('last-id', 0)
        new_last_id = last_id + 1
        data['last-id'] = new_last_id
        haremDB.save(data)
        haremDB.create_harem(new_last_id)
        return new_last_id

    @staticmethod
    def create_harem(harem_id=None):
        data = haremDB.load()
        if harem_id is None:
            harem_id = haremDB.create_new_harem_id()
        harem_id = str(harem_id)
        if harem_id not in data['harems']:
            data['harems'][harem_id] = {}
            haremDB.save(data)
            return harem_id
        return False

    @staticmethod
    def remove_harem(user_id):
        data = haremDB.load()
        user_id = str(user_id)
        if user_id in data['harems']:
            del data['harems'][user_id]
            haremDB.save(data)
            return True
        return False

    @staticmethod
    def get_waifu_count(user_id, waifu_id):
        data = haremDB.load()
        user_id = str(user_id)
        waifu_id = str(waifu_id)
        try:
            return data['harems'].get(user_id, {}).get(waifu_id, 0)
        except Exception as e:
            logger.error(f"Error getting waifu count for user_id {user_id}, waifu_id {waifu_id}: {e}")
            return 0

    @staticmethod
    def add_waifu_to_harem(harem_id, waifu_id):
        data = haremDB.load()
        harem_id = str(harem_id)
        waifu_id = str(waifu_id)

        if harem_id not in data['harems']:
            haremDB.create_harem(harem_id)

        if waifu_id not in data['harems'][harem_id]:
            data['harems'][harem_id][waifu_id] = 1
        else:
            data['harems'][harem_id][waifu_id] += 1
        haremDB.save(data)
        return True

    @staticmethod
    def remove_waifu_from_harem(harem_id, waifu_id):
        data = haremDB.load()
        harem_id = str(harem_id)
        waifu_id = str(waifu_id)
        if harem_id in data['harems'] and waifu_id in data['harems'][harem_id]:
            del data['harems'][harem_id][waifu_id]
            haremDB.save(data)
            return True
        return False
    
    def gift_waifu(user_harem_id,target_harem_id,waifu_id):
        data = haremDB.load()
        user_harem_id = str(user_harem_id)
        target_harem_id = str(target_harem_id)
        waifu_id = str(waifu_id)

        if user_harem_id not in data['harems'] or target_harem_id not in data['harems']:
            return False

        if waifu_id not in data['harems'][user_harem_id]:
            return False

        count = data['harems'][user_harem_id][waifu_id]
        if count > 1:
            data['harems'][user_harem_id][waifu_id] -= 1
        else:
            del data['harems'][user_harem_id][waifu_id]

        if waifu_id not in data['harems'][target_harem_id]:
            data['harems'][target_harem_id][waifu_id] = count
        else:
            data['harems'][target_harem_id][waifu_id] += count

        haremDB.save(data)
        return True