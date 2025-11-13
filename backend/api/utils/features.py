#generate peaks and extract features from audio
import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Dict


class AudioFeatureExtractor():
    def __init__(self):
        self.scaler = StandardScaler()

    def generate_peaks(self, audio_path, sr=22050, hop_length=512):
        """Generate waveform peaks from an audio file."""
        y, _ = librosa.load(audio_path, sr=sr)
        # Compute the amplitude envelope
        envelope = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        return envelope.tolist()
    
    def generate_peaks_2(self, audio_path: str,sr:int = 22050, num_peaks:int = 960) -> np.array:
        """Generate waveform peaks from an audio file."""
        # Load audio file
        signal, sr = librosa.load(audio_path, sr=sr)

        # Compute the absolute values of the signal
        abs_signal = np.abs(signal)

        # Compute the maximum value of the signal
        max_value = np.max(abs_signal)

        # Normalize the signal to values between 0 and 1
        normalized_signal = abs_signal / max_value

        # Split the signal into num_peaks chunks
        chunk_size = len(normalized_signal) // num_peaks
        chunks = [normalized_signal[i:i + chunk_size] for i in range(0, len(normalized_signal), chunk_size)]

        # Compute the maximum value of each chunk
        peaks = [np.max(chunk) for chunk in chunks]

        # Scale the peaks to values between 0 and 100
        scaled_peaks = [int(peak * 100) for peak in peaks]

        return scaled_peaks


    def extract_features(self, audio_path: str,sr = 22050) -> Dict:
        """Extract comprehensive audio features for similarity analysis"""

        y, sr = librosa.load(audio_path, sr=sr)
        features ={}

        #tempo
        features['tempo'] = librosa.beat.tempo(y=y, sr=sr)[0] #will be librosa.rhythm.beat.tempo in future versions

        #spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid_mean'] = np.mean(spectral_centroids) 
        features['spectral_centroid_std'] = np.std(spectral_centroids) 

        #MFCC mel frequency cepstral coeffcients
        mfccs = librosa.feature.mfcc(y = y, sr = sr, n_mfcc=13)  

        for i in range(13):
            features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i}_std'] = np.std(mfccs[i])

        #chroma features
        chroma_stft = librosa.feature.chroma_stft(y = y, sr=sr)
        features['chroma_stft_mean'] = np.mean(chroma_stft)

        #rythm features
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        features['onset_strength_mean'] = np.mean(onset_env)

        #zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features['zcr_mean'] = np.mean(zcr)

        return features

    def create_feature_vector(self, features:Dict) -> np.array:
        "Convert features dictionary into normalized vectors"
        feature_vector = np.array(list(features.values()))
        return self.scaler.fit_transform(feature_vector.reshape(-1, 1))[0]