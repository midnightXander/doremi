from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from werkzeug import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import numpy,openl3
import soundfile as sf
from .models import *
import librosa

# preload smaller/faster model once at import 
MODEL = openl3.models.load_audio_embedding_model(input_repr="mel128", content_type="music", embedding_size=512)

def get_audio_embedding(file_path, target_sr = 22050, duration=None):
    audio, sr = sf.read(file_path)

    #convert to mono and resample to target_sr for much faster processing
    if audio.ndim > 1:
        audio = numpy.mean(audio, axis=1)
    if sr != target_sr:
        audio = librosa.resample(audio.astype(numpy.float32), orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    # if duration is not None:
    #     max_length = int(target_sr * duration)
    #     audio = audio[:max_length]    
    if duration:
        # max_length = int(target_sr * duration)
        # if len(audio) > max_length:
        #     audio = audio[:max_length]
        # else:
        #     padding = max_length - len(audio)
        #     audio = numpy.pad(audio, (0, padding), 'constant')
        audio = audio[: int(duration * sr)]

    emb, ts = openl3.get_audio_embedding(audio, sr,
                                         content_type = 'music',
                                         input_repr='mel128',
                                         embedding_size=512,
                                         model=MODEL,
                                         center=True,
                                         hop_size=0.1)
    return emb.mean(axis=0).tolist()

class Upload(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            song = serializer.save()
            file_path = song.file.path
            try:
                emb = get_audio_embedding(file_path, target_sr = 22050, duration=15)  # optionally limit duration
                song.embedding = emb
                song.save()
                return JsonResponse({"status": "success", "songs": [serializer.data]}, status=201, safe=False)
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=500, safe=False)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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