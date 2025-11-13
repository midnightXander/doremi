from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from werkzeug import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import openl3
import numpy as np
import soundfile as sf
from .models import *
import librosa
from .utils.relevant_part import extract_most_relevant_part
import faiss
from pathlib import Path
import json
from .utils.embedding import get_audio_embedding
from .utils.features import AudioFeatureExtractor
from .utils.waveform_similarity import WaveformSimilarity

extractor = AudioFeatureExtractor()
waveform_sim = WaveformSimilarity()

# preload smaller/faster model once at import 
MODEL = openl3.models.load_audio_embedding_model(input_repr="mel128", content_type="music", embedding_size=512)
OUT_DIR = Path(__file__).resolve().parents[1] / "api/data"
OUT_DIR.mkdir(parents = True, exist_ok=True)
EMB_FILE = OUT_DIR / "local_embeddings.npy"
META_FILE = OUT_DIR / "local_metadata.jsonl"

emb_list = list(np.load(EMB_FILE, allow_pickle=True))
meta_list = []

with open(META_FILE, "r", encoding="utf-8") as mf:
        for meta in mf:
            meta_list.append(json.loads(meta))
            


# def get_audio_embedding(file_path, target_sr = 22050, duration=None):
#     print(file_path)
#     audio, sr = sf.read(file_path)
#     # relevant_part, relevant_sr = extract_most_relevant_part(file_path, 15)
#     # print(len(audio), sr)
#     # print(len(relevant_part), relevant_sr)

#     #convert to mono and resample to target_sr for much faster processing
#     if audio.ndim > 1:
#         audio = np.mean(audio, axis=1)
#     if sr != target_sr:
#         audio = librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=target_sr)
#         sr = target_sr

#     # if duration is not None:
#     #     max_length = int(target_sr * duration)
#     #     audio = audio[:max_length]    
#     if duration:
#         max_length = len(audio)
#         # max_length = int(target_sr * duration)
#         # if len(audio) > max_length:
#         #     audio = audio[:max_length]
#         # else:
#         #     padding = max_length - len(audio)
#         #     audio = np.pad(audio, (0, padding), 'constant')
#         audio = audio[max_length//2 : max_length//2 + int(duration * sr)]

#     emb, ts = openl3.get_audio_embedding(audio, sr,
#                                          content_type = 'music',
#                                          input_repr='mel128',
#                                          embedding_size=512,
#                                          model=MODEL,
#                                          center=True,
#                                          hop_size=0.1)
#     return emb.mean(axis=0).tolist()

class Upload(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            song = serializer.save()
            file_path = song.file.path
            emb = get_audio_embedding(file_path, target_sr = 22050, duration=15, model = MODEL)  # optionally limit duration
            song.embedding = emb
            song.save()
            return JsonResponse({"status": "success", "songs": [serializer.data]}, status=201, safe=False)
            # try:
            #     emb = get_audio_embedding(file_path, target_sr = 22050, duration=15)  # optionally limit duration
            #     song.embedding = emb
            #     song.save()
            #     return JsonResponse({"status": "success", "songs": [serializer.data]}, status=201, safe=False)
            # except Exception as e:
            #     return JsonResponse({"status": "error", "message": str(e)}, status=500, safe=False)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SimilarSongs(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"status":"error","message":"No file provided"}, status = 400, safe = False)
        
        #save uploaded file temporarily
        temp_path = OUT_DIR / "temp_uploaded_file"
        with open(temp_path, "wb+") as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
        
        
        try:
            emb = get_audio_embedding(temp_path, target_sr = 22050, duration=15, model = MODEL)  # optionally limit duration
            emb_np = np.array(emb).astype('float32').reshape(1, -1)

            #build faiss index
            dimension = emb_np.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(emb_list).astype('float32'))

            k = 5  # number of nearest neighbors
            distances, indices = index.search(emb_np, k)

            similar_songs = []
            for idx in indices[0]:
                similar_songs.append(meta_list[idx])

            print("Similar songs found:", similar_songs)

            return JsonResponse({"status":"success","similar_songs":similar_songs}, status = 200, safe = False)
            
            
            # peaks = extractor.generate_peaks_2(audio_path=temp_path)
            # print("Peaks: ",peaks[:100])
            # features = extractor.extract_features(audio_path=temp_path)
            # print("Features: ",features)
            # return JsonResponse({"status":"success"}, status = 200, safe = False)
        except Exception as e:
            return JsonResponse({"status":"error","message":str(e)}, status = 500, safe = False)
        finally:
            if temp_path.exists():
                temp_path.unlink()  # delete temporary file


class Newsletter(APIView):
    def post(self, request, action):
        email = request.data.get('email')
        print("Received newsletter subscription from:", email)
        if action == 'subscribe':
            try:
                new_subscription = NewsletterSubscription.objects.create(email=email)
                new_subscription.save()
            except Exception as e:
                return JsonResponse({"status":"error","message":str(e)}, status = 400, safe = False)    
        return JsonResponse({"status":"subscribed"}, status = 200, safe = False)    