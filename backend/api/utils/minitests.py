import requests

#get access tokens for spotify api by client credentials flow. 
"""
curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"

"""
r = requests.post("https://accounts.spotify.com/api/token", 
                  headers={"Content-Type": "application/x-www-form-urlencoded"},
                  data={"grant_type":"client_credentials",
                        "client_id":"c1b7d2aa4cc5456c8635c7da3c0d68f2",
                        "client_secret":"b17d4c03bb994f44ae2126aead23f43d"},
                   timeout=30)

r.raise_for_status()
print(r.status_code, r.json())

#test artists endpoint
"""
curl "https://api.spotify.com/v1/artists/4Z8W4fKeB5YxbusRsdQVPb" \
     -H "Authorization: Bearer  BQDBKJ5eo5jxbtpWjVOj7ryS84khybFpP_lTqzV7uV-T_m0cTfwvdn5BnBSKPxKgEb11"
"""

# r = requests.get("https://api.spotify.com/v1/search?q=dams&type=artist",
#                  headers={"Authorization": "Bearer BQCeoTGQZegC0W0dLxmObThVXiymGbSmiXS_PVlTnx8JOj4MpONIY8ywphb7TSA6r25lSq2C1dRsqbQTJXetKASZQMvQCqGRSqbhT-TcXlyo6dd0a8vWS7Yv7Bqzag2pIQe9JJUCS6k"},
#                  timeout=30)
# r.raise_for_status()
# print(r.status_code, r.json())


#extract audio features from waveform peaks and calculate similarity
# class WaveformSimilarity:
#     def __init__(self, threshold=0.5):
#         self.threshold = threshold

#     def extract_features(self, waveform):
#         # Calculate FFT of the waveform
#         fft_values = fft(waveform)
#         magnitude = np.abs(fft_values)
#         return magnitude[:len(magnitude) // 2]  # Return only the positive frequencies

#     def calculate_similarity(self, waveform1, waveform2):
#         features1 = self.extract_features(waveform1)
#         features2 = self.extract_features(waveform2)

#         # Normalize features
#         norm1 = np.linalg.norm(features1)
#         norm2 = np.linalg.norm(features2)

#         if norm1 == 0 or norm2 == 0:
#             return 0.0

#         normalized_features1 = features1 / norm1
#         normalized_features2 = features2 / norm2

#         # Calculate cosine similarity
#         similarity = 1 - spatial.distance.cosine(normalized_features1, normalized_features2)
#         return similarity

#     def is_similar(self, waveform1, waveform2):
#         similarity_score = self.calculate_similarity(waveform1, waveform2)
#         return similarity_score >= self.threshold