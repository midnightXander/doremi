import json
import numpy as np
from pathlib import Path
from features import AudioFeatureExtractor
from waveform_similarity import WaveformSimilarity

extractor = AudioFeatureExtractor()
waveform_sim = WaveformSimilarity()

OUT_DIR = Path(__file__).resolve().parents[1] / "data"
TRACKS_FILE = OUT_DIR / "jamendo_tracks.jsonl"

PEAKS_FEATURES_FILE = OUT_DIR / "local_peaks_features.jsonl"
features_list = []
limit = 1500

with open(PEAKS_FEATURES_FILE, "r", encoding="utf-8") as mf:
        for meta in mf:
            features_list.append(json.loads(meta))
print(len(features_list))

with open(TRACKS_FILE, "r", encoding="utf-8") as mf:
        i = 0
        for track in mf:
            track_data = json.loads(track)
            id = track_data.get("id")
            waveform = json.loads(track_data.get("waveform"))
            peaks = np.array(waveform['peaks'])

            #normalize to 0-1
            norm_peaks = peaks / max(abs(peaks))
            features = waveform_sim.extract_features_from_peaks(norm_peaks)
            
            if id not in [feature['id'] for feature in features_list]:
                features_list.append({"id": id, "features": features})
                print(f"Extracted features for track ID {id}: {features}")
                with open(PEAKS_FEATURES_FILE, "w", encoding="utf-8") as mf:
                    for f in features_list:
                        mf.write(json.dumps(f, ensure_ascii=False) + "\n")
                
                i += 1
                if(i == limit): break
            


