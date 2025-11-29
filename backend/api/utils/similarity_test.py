import json
import numpy as np
from pathlib import Path
from features import AudioFeatureExtractor
from waveform_similarity import WaveformSimilarity
import os

extractor = AudioFeatureExtractor()
waveform_sim = WaveformSimilarity()

OUT_DIR = Path(__file__).resolve().parents[1] / "data"
TRACKS_FILE = OUT_DIR / "jamendo_tracks.jsonl"
PEAKS_FEATURES_FILE = OUT_DIR / "local_peaks_features.jsonl"
SONGS_FOLDER_PATH = "E:\music"
features_list = []
tracks = []

with open(PEAKS_FEATURES_FILE, "r", encoding="utf-8") as mf:
        for meta in mf:
            features_list.append(json.loads(meta))

with open(TRACKS_FILE, "r", encoding="utf-8") as mf:
        i = 0
        for track in mf:
            tracks.append(json.loads(track))

def find_similar(filename):
    filepath = os.path.join(SONGS_FOLDER_PATH, filename)
    peaks = extractor.generate_peaks_2(filepath)
    ref_features = waveform_sim.extract_features_from_peaks(peaks)

    similars = []
    for i, feature in enumerate(features_list):
        sim = waveform_sim.calculate_similarity(ref_features, feature['features'])
        similars.append((feature['id'], sim))
        #print(f"Similarity between track 0 and track {feature['id']}: {sim}")

    top_5 = sorted(similars, key=lambda x: x[1], reverse=True)[:5]
    print(f"Top 5 most similar tracks to {filename}:", top_5)

    #find the tracks meta data in tracks list with id
    similar_tracks = []
    for similar in top_5:
        track_id = similar[0]
        track_meta = next(({ 'name': track['name'], 'audiodownload' : track.get('audiodownload') if track.get('audiodownload') else track.get('audio') } for track in tracks if track['id'] == track_id), None)
        similar_tracks.append((track_id, track_meta))
        # print(f"Track ID: {track_id}, Meta: {track_meta}")

    return similar_tracks    
     

filename = "Muni Long - Pain (Official Video)(MP3_160K).mp3"
similar_songs = find_similar(filename)
print(similar_songs)
