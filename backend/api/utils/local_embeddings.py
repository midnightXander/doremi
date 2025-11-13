import json
import os
import numpy as np
from embedding import get_audio_embedding  # reuse your function
from pathlib import Path
import openl3

MODEL = openl3.models.load_audio_embedding_model(input_repr="mel128", content_type="music", embedding_size=512)

SONGS_FOLDER_PATH = "E:\music"
SONGS = []

OUT_DIR = Path(__file__).resolve().parents[1] / "data"
OUT_DIR.mkdir(parents = True, exist_ok=True)
EMB_FILE = OUT_DIR / "local_embeddings.npy"
META_FILE = OUT_DIR / "local_metadata.jsonl"

emb_list = list(np.load(EMB_FILE, allow_pickle=True))
meta_list = []
print(len(emb_list))

with open(META_FILE, "r", encoding="utf-8") as mf:
        for meta in mf:
            meta_list.append(json.loads(meta))
            
            
last_id = meta_list[-1]['id']
print(last_id)
#iterate through the music folder and get embeddiings for .mp3 files
for idx, filename in enumerate(os.listdir(SONGS_FOLDER_PATH)):
    file_path = os.path.join(SONGS_FOLDER_PATH, filename)
    if os.path.isfile(file_path) and filename.endswith(".mp3") and filename not in [meta['filename'] for meta in meta_list]:
        try:
            emb = get_audio_embedding(file_path, target_sr = 22050, duration = 15, model = MODEL)
            emb_list.append(emb)
            id = int(last_id) + 1
            meta_list.append({"id": str(id), "filename": filename, "file_path": file_path})
            
            #save embeddings and metadata for each file
            emb_matrix = np.vstack(emb_list)
            np.save(EMB_FILE, np.array(emb_list))
            with open(META_FILE, "w", encoding="utf-8") as mf:
                for m in meta_list:
                    mf.write(json.dumps(m, ensure_ascii=False) + "\n")

            print(f"Embedding for {filename}: {emb[:5]}...")  # Print first 5 values of the embedding
        except Exception as e:
            print("Failed ", filename, e)
