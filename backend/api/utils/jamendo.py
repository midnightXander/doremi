# jamendo api_integration.py
import requests
from typing import List, Dict

class JamendoMusicAPI:
    def __init__(self, client_id: str, base_url: str = "https://api.jamendo.com/v3.0"):
        self.base_url = base_url
        self.client_id = client_id
        self.params = {'client_id': self.client_id}

        #add necessary headers to simulate browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
        }

        # if self.api_key:
        #     self.headers = {'Authorization': f'Bearer {api_key}'}
            
    
    def get_song_data(self, song_id: str) -> Dict:
        """Fetch individual song data including waveform peaks"""
        endpoint = f"{self.base_url}/tracks/file/{song_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()['results'][0]
    
    def get_batch_songs(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """Fetch songs in batches for initial database population"""
        endpoint = f"{self.base_url}/tracks/"
        params = self.params.copy()
        params.update({'limit': limit, 'offset': offset, 'include': 'musicinfo', 'format': 'jsonpretty', 'groupby': 'artist_id'})
        # try:
        response = requests.get(endpoint, params=params, headers=self.headers)
        songs =  response.json()['results']
        return songs
        # except Exception as e:
        #     print("Error fetching batch songs:", e)
        #     return []
    
    def search_songs(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search songs by various criteria"""
        endpoint = f"{self.base_url}/search"
        params = {'q': query}
        if filters:
            params.update(filters)
        response = requests.get(endpoint, params=params)
        return response.json()['results']