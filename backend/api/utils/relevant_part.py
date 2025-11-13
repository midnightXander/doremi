import soundfile as sf
import numpy as np

def extract_most_relevant_part(file_path, duration=15):
    """
    Return the most 'relevant' audio segment of `duration` seconds:
    - convert to mono
    - compute short-term energy with a centered window
    - pick the window centered on the max energy
    - pad with zeros if audio is shorter than requested duration
    """
    audio, sr = sf.read(file_path)

    # Convert to mono if needed
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    audio = np.asarray(audio, dtype=np.float32)

    # Desired window size in samples
    window_size = int(max(1, duration * sr))

    n = len(audio)
    if n <= window_size:
        # pad to requested length
        padded = np.zeros(window_size, dtype=np.float32)
        padded[:n] = audio
        return padded, sr

    # short-term energy (centered)
    energy = audio * audio
    print(energy)
    # use 'same' so the energy array aligns with audio indices
    kernel = np.ones(window_size, dtype=np.float32)
    print(kernel)
    energy_envelope = np.convolve(energy, kernel, mode='same')

    # find index of maximum energy and center the window there
    peak_idx = int(np.argmax(energy_envelope))

    start = peak_idx - window_size // 2
    end = start + window_size

    # clamp to bounds
    if start < 0:
        start = 0
        end = window_size
    if end > n:
        end = n
        start = n - window_size

    print(start, end)    

    relevant_audio = audio[start:end]

    return relevant_audio, sr
