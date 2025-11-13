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
tracks = []
with open(PEAKS_FEATURES_FILE, "r", encoding="utf-8") as mf:
        for meta in mf:
            features_list.append(json.loads(meta))

with open(TRACKS_FILE, "r", encoding="utf-8") as mf:
        i = 0
        for track in mf:
            tracks.append(json.loads(track))

# test_peaks = []
# with open(TRACKS_FILE, "r", encoding="utf-8") as mf:
#         i = 0
#         for track in mf:
#             track_data = json.loads(track)
#             waveform = json.loads(track_data.get("waveform"))
#             test_peaks = waveform['peaks']

#             #normalize to 0-1
#             test_peaks = np.array(test_peaks) / max(abs(np.array(test_peaks)))
#             print(len(test_peaks), test_peaks[:10])
#             i += 1
#             if(i == 30): break
            # print(test_peaks[:100])
            #features = waveform_sim.extract_features_from_peaks(test_peaks)
            #print(features)
            #break

# test similarity comparison with first entry in features list and get top 5 most similar
ref_features = features_list[0]['features']

similars = []
for i, feature in enumerate(features_list[1:], start=1):
    sim = waveform_sim.calculate_similarity(ref_features, feature['features'])
    similars.append((feature['id'], sim))
    print(f"Similarity between track 0 and track {feature['id']}: {sim}")

top_5 = sorted(similars, key=lambda x: x[1], reverse=True)[:5]
print("Top 5 most similar tracks to track 0:", top_5)

#find the tracks meta data in tracks list with id
for similar in top_5:
    track_id = similar[0]
    track_meta = next((track for track in tracks if track['id'] == track_id), None)
    print(f"Track ID: {track_id}, Meta: {track_meta}")

