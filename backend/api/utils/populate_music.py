from jamendo import JamendoMusicAPI
from pathlib import Path
import json

#get songs in batch and populate database(json file first)
OUT_DIR = Path(__file__).resolve().parents[1] / "data"
JAMENDO_TRACKS_FILE = OUT_DIR / "jamendo_tracks.jsonl"

client_id = "5ff3890d"
api = JamendoMusicAPI(client_id=client_id)

def is_track_in_file(track_id: str, file_path: Path) -> bool:
    """Check if a track ID already exists in the given JSONL file."""
    if not file_path.exists():
        return False
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("id") == track_id:
                return True
    return False

BATCH_SIZE = 200
offset = 4500

#sample test
# print(api.get_batch_songs(limit=10, offset=offset))

while offset < 10000:  # Adjust the upper limit as needed
    songs = api.get_batch_songs(limit=BATCH_SIZE, offset=offset)
    if not songs:
        break  # No more songs to fetch
    with open(JAMENDO_TRACKS_FILE, "a", encoding="utf-8") as f:
        for song in songs:
            if not is_track_in_file(song['id'], JAMENDO_TRACKS_FILE) and song.get('waveform'): #ensure to get only tracks with waveform info
                f.write(json.dumps(song, ensure_ascii=False) + "\n")
    print(f"Fetched and saved {len(songs)} songs from offset {offset}")        
    offset += BATCH_SIZE
