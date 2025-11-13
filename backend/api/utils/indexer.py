import json
import os
import tempfile
import requests
import numpy as np
#import hnswlib
from yt_dlp import YoutubeDL
from embedding import get_audio_embedding  # reuse your function
from pathlib import Path
import openl3, numpy

MODEL = openl3.models.load_audio_embedding_model(input_repr="mel128", content_type="music", embedding_size=512)

SOURCES = [

]

OUT_DIR = Path(__file__).resolve().parents[1] / "data"
OUT_DIR.mkdir(parents = True, exist_ok=True)
EMB_FILE = OUT_DIR / "embeddings.npy"
META_FILE = OUT_DIR / "metadata.jsonl"
INDEX_FILE = OUT_DIR / "hnsw_index.bin"

emb_list = []
meta_list = []

def download_audio_to_file(url, dest_path):
    if "youtube" in url or "youtu.be" in url:
        ydl_opts = {"format": "bestaudio/best", "outtmpl" : str(dest_path), "quiet" : True, "no_warnings":True }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return str(dest_path)
    # generic file
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(1024 * 32):
            if chunk:
                f.write(chunk)
    return str(dest_path)

for idx, item in enumerate(SOURCES):
    tmpf = tempfile.NamedTemporaryFile(delete = False, suffix = ".mp3")
    tmpf.close()
    try:
        download_audio_to_file(item['url'], tmpf.name)
        emb = get_audio_embedding(tmpf.name, target_sr = 22050, duration = 10, model = MODEL)
        emb_list.append(np.array(emb, dtype=np.float32))
        meta = { "id" : item.get('id', str(idx)), "url": item['url'], "title": item.get('title') }
        meta_list.append(meta)
        print("Indexed", meta["id"])
    except Exception as e:
        print("Failed ", item.get("url"), e)       
    finally:
        try:
            os.unlink(tmpf.name)
        except Exception:
            pass                     
        

if not emb_list:
    raise SystemExit("No embeddings produced")

emb_matrix = np.vstack(emb_list)
np.save(EMB_FILE, emb_matrix)
with open(META_FILE, "w", encoding = 'utf-8') as mf:
    for m in meta_list:
        mf.write(json.dumps(m, ensure_ascii=False)+ "\n")

# build hnswlib index
# dim = emb_matrix.shape[1]
# num_elements = emb_matrix.shape[0]
# p = hnswlib.Index(space = 'cosine', dim = dim)
# p.init_index(max_elements = num_elements, ef_construction = 200, M=64)
# p.add_items(emb_matrix, np.arrange(num_elements))
# p.set_ef(50)
# p.save_index(str(INDEX_FILE))
# print("Index saved: ", INDEX_FILE)