import json
import random
from typing import Dict, Optional, Union

OSHINOKO_FILE = "data/oshinoko.json"

class EnhancedOshinokoDB:
    @staticmethod
    def _load_data() -> Dict:
        try:
            with open(OSHINOKO_FILE, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'users': {}, 'gifs': {}}

    @staticmethod
    def _save_data(data: Dict) -> None:
        with open(OSHINOKO_FILE, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def get_idol(user_id: Union[int, str]) -> Optional[str]:
        data = EnhancedOshinokoDB._load_data()
        user_id = str(user_id)
        return data.get('users', {}).get(user_id, {}).get('idol')

    @staticmethod
    def set_idol(user_id: Union[int, str], idol: str) -> None:
        data = EnhancedOshinokoDB._load_data()
        user_id = str(user_id)
        
        if 'users' not in data:
            data['users'] = {}
        
        if user_id not in data['users']:
            data['users'][user_id] = {}
            
        data['users'][user_id]['idol'] = idol
        EnhancedOshinokoDB._save_data(data)

    @staticmethod
    def set_video(idol: str, video_id: str, is_win: bool) -> None:
        data = EnhancedOshinokoDB._load_data()
        idol = str(idol)
        
        if 'gifs' not in data:
            data['gifs'] = {}
        
        if idol not in data['gifs']:
            data['gifs'][idol] = {"wingif": [], "losegif": []}
            
        key = 'wingif' if is_win else 'losegif'
        if video_id not in data['gifs'][idol][key]:
            data['gifs'][idol][key].append(video_id)
            EnhancedOshinokoDB._save_data(data)

    @staticmethod
    def get_video(idol: str, is_win: bool) -> Optional[str]:
        data = EnhancedOshinokoDB._load_data()
        idol = str(idol)
        key = 'wingif' if is_win else 'losegif'
        videos = data.get('gifs', {}).get(idol, {}).get(key, [])
        return random.choice(videos) if videos else None