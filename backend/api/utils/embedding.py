import numpy,openl3
import soundfile as sf
import librosa

def get_audio_embedding(file_path, target_sr = 22050, duration=None, model=None):
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
        max_length = len(audio)
        # max_length = int(target_sr * duration)
        # if len(audio) > max_length:
        #     audio = audio[:max_length]
        # else:
        #     padding = max_length - len(audio)
        #     audio = numpy.pad(audio, (0, padding), 'constant')
        
        #get the center part of the audio
        audio = audio[max_length//2 : max_length//2 + int(duration * sr)]

    emb, ts = openl3.get_audio_embedding(audio, sr,
                                         content_type = 'music',
                                         input_repr='mel128',
                                         embedding_size=512,
                                         model=model,
                                         center=True,
                                         hop_size=0.1)
    return emb.mean(axis=0).tolist()