import numpy as np
from scipy.fft import fft
from scipy import spatial,stats
from scipy.signal import correlate
import math

#extract audio features from waveform peaks and calculate similarity
class WaveformSimilarity:
    def __init__(self):
        self.feature_weights = {
            "rhythm_pattern" : 0.4,
            'dynamic_range' : 0.3,
            'spectral_characteristics' : 0.3 
        }

    def extract_features_from_peaks(self, peaks):
        #extract musical features from waveform peaks
        peaks_array = np.array(peaks)


        features = {}

        #1.Rhythm and beat analysis
        features['rhythm_pattern'] = self.analyze_rhythm(peaks_array)     
        
        #2.Dynamic range and loudness
        features['dynamic_range'] = self.analyze_dynamics(peaks_array)

        #3.Spectral characteristics
        features['spectral_characteristics'] = self.analyze_spectral(peaks_array)

        #3.Statistical features
        features['statistical'] = self.analyze_statistics(peaks_array)

        return features
    
    def analyze_rhythm(self, peaks):
        """Extract rhythmic patterns from peaks"""
        #Normalize peaks
        normalized_peaks = ((peaks - np.min(peaks)) / (np.max(peaks) - np.min(peaks)))

        #find prominent beats (high amplitude beats)
        threshold = np.mean(normalized_peaks) + np.std(normalized_peaks)
        beat_positions = np.where(normalized_peaks > threshold)[0]

        #calculate inter-beat intervals for tempo estimation
        if len(beat_positions) > 1:
            intervals = np.diff(beat_positions)
            rhythm_consistency = 1.0 / (np.std(intervals) + 1e-6) if np.std(intervals) != 0 else 1.0
        else:
            rhythm_consistency = 0

        #overall rhythmic complexity 
        rhythmic_complexity = np.std(normalized_peaks)

        #tempo
        tempo = 60.0 / (np.mean(np.diff(beat_positions)) + 1e-6) if len(beat_positions) > 1 else 0

        return {
            'beat_density': len(beat_positions) / len(peaks),
            'rhythm_consistency': min(rhythm_consistency, 10), #cap extreme values
            'rhythmic_complexity': rhythmic_complexity,
            'tempo' : tempo
        }

    def analyze_dynamics(self, peaks):
        """Analyze loudness  and dynamic range"""
        return {
            'average_loudness' : np.mean(peaks),
            'dynamic_range' : np.max(peaks) - np.min(peaks),
            'loudness_variance' : np.var(peaks),
            'peak_intensity' : np.max(peaks),
        }        
    
    def analyze_spectral(self, peaks):
        """Analyze frequency domain characteristics"""
        #Apply FFT to get frequency domain characteristics
        fft_result = np.abs(fft(peaks))
        fft_result = fft_result[:len(fft_result//2)] #taking first half

        #Spectral features
        spectral_centroid = np.sum(fft_result * np.arange(len(fft_result))) / np.sum(fft_result)
        spectral_spread = np.sqrt(np.sum((np.arange(len(fft_result)) - spectral_centroid)**2 * fft_result) / np.sum(fft_result))

        return {
            "spectral_centroid" : spectral_centroid,
            "spectral_spread" : spectral_spread,
            "spectral_flatness" : self.calculate_spectral_flatness(fft_result)
        }
    
    def analyze_statistics(self, peaks):
        """Extract statistical features"""
        return {
            'skewness': self.calculate_skewness(peaks),
            'kurtosis': self.calculate_kurtosis(peaks),
            'zero_crossing_rate': self.calculate_zero_crossing_rate(peaks),
            'autocorrelation': self.calculate_autocorrelation(peaks)
        }
    
    def calculate_skewness(self, peaks):
        """Calculate the skewness of the waveform peaks"""
        if len(peaks) < 3:
            return 0
        return float(stats.skew(peaks))
    
    def calculate_kurtosis(self,peaks):
        """Calculate the kurtosis of the waveform peaks"""
        if len(peaks) < 4:
            return 0
        return float(stats.kurtosis(peaks))
    
    def calculate_zero_crossing_rate(self, peaks):
        """Calculate the zero-crossing rate of the waveform"""
        if len(peaks) < 2:
            return 0
        
        # Normalize peaks around zero
        normalized_peaks = peaks - np.mean(peaks)
        
        # Count zero crossings
        zero_crossings = np.where(np.diff(np.sign(normalized_peaks)))[0]
        return len(zero_crossings) / (len(peaks) - 1)
    
    def calculate_autocorrelation(self, peaks, max_lag=None):
        """Calculate autocorrelation features"""
        if len(peaks) < 10:
            return {'max_autocorr': 0, 'autocorr_peak_ratio': 0}
        
        if max_lag is None:
            max_lag = min(100, len(peaks) // 4)

        # Normalize the signal
        normalized_peaks = peaks - np.mean(peaks)
        
        # Calculate autocorrelation
        autocorr = correlate(normalized_peaks, normalized_peaks, mode='full')
        autocorr = autocorr[len(autocorr)//2:]  # Take only positive lags
        autocorr = autocorr[:max_lag]  # Limit to max_lag
        
        # Normalize autocorrelation
        autocorr = autocorr / autocorr[0] if autocorr[0] != 0 else autocorr

        # Find the maximum autocorrelation (excluding lag 0)
        if len(autocorr) > 1:
            max_autocorr = np.max(autocorr[1:])
            
            # Calculate peak-to-average ratio in autocorrelation
            autocorr_mean = np.mean(autocorr[1:])
            autocorr_peak_ratio = max_autocorr / autocorr_mean if autocorr_mean > 0 else 0
        else:
            max_autocorr = 0
            autocorr_peak_ratio = 0
        
        return {
            'max_autocorr': float(max_autocorr),
            'autocorr_peak_ratio': float(autocorr_peak_ratio),
            'autocorr_values': autocorr.tolist()[:10]  # First 10 values for comparison
        }

    def calculate_spectral_flatness(self, fft_magnitude):
        """Calculate spectral flatness (tonality vs noisiness)"""
        if len(fft_magnitude) == 0 or np.any(fft_magnitude <= 0):
            return 0
        
        # Geometric mean
        geometric_mean = np.exp(np.mean(np.log(fft_magnitude)))
        # Arithmetic mean
        arithmetic_mean = np.mean(fft_magnitude)
        
        return geometric_mean / arithmetic_mean if arithmetic_mean > 0 else 0    
    
    def calculate_similarity(self, features1, features2):
        """Calculate overall similarity between the two sets of features"""

        # # Ensure we have valid peak data
        # if len(peaks1) < 10 or len(peaks2) < 10:
        #     return 0.0
        
        # #Extract features from both peak sets
        # features1 = self.extract_features_from_peaks(peaks1)
        # features2 = self.extract_features_from_peaks(peaks2)

        similarities = {}

        #compare each feature category
        for category in features1.keys():
            if category == 'rhythm_pattern':
                similarities[category] = self.compare_rhythm_patterns(
                    features1[category], features2[category]
                )
            elif category == 'dynamic_range':
                similarities[category] = self.compare_dynamics(
                    features1[category], features2[category]
                )
            elif category == 'spectral_characteristics':
                similarities[category] = self.compare_spectral(
                    features1[category], features2[category]
                )
            else:
                similarities[category] = self.compare_statistical(
                    features1[category], features2[category]
                )

        #weighted combination of all similarities
        overall_similarities = sum(
            similarities[category] * weight for category, weight in self.feature_weights.items()
        )            
        return overall_similarities
    
    def compare_rhythm_patterns(self, rhythm1, rhythm2):
        """compare rhythmic characteristics"""
        rhythm_similarity = 0
        for key in rhythm1.keys():
            val1, val2 = rhythm1[key], rhythm2[key]
            similarity = 1 - abs(val1-val2) /  (max(val1, val2) + 1e-6)
            rhythm_similarity += similarity

        return rhythm_similarity / len(rhythm1) 

    def compare_dynamics(self, dynamics1, dynamics2):
        "compare dynamic range and loudness characteristics"

        similarity_score = 0
        total_weight = 0

        #compare average loudness
        loudness1, loudness2 = dynamics1['average_loudness'], dynamics2['average_loudness']
        loudness_similarity = 1 - abs(loudness1 - loudness2) / (max(abs(loudness1), abs(loudness2)) + 1e-8)

        similarity_score += loudness_similarity * 0.3
        total_weight += 0.3

        # Compare dynamic range
        range1, range2 = dynamics1['dynamic_range'], dynamics2['dynamic_range']
        if max(range1, range2) > 0:
            range_sim = 1 - abs(range1 - range2) / max(range1, range2)
        else:
            range_sim = 1.0 if range1 == range2 else 0.0
        similarity_score += range_sim * 0.3
        total_weight += 0.3

        # Compare loudness variance
        var1, var2 = dynamics1['loudness_variance'], dynamics2['loudness_variance']
        if max(var1, var2) > 0:
            var_sim = 1 - abs(var1 - var2) / max(var1, var2)
        else:
            var_sim = 1.0 if var1 == var2 else 0.0
        similarity_score += var_sim * 0.2
        total_weight += 0.2

        # Compare peak intensity
        peak1, peak2 = dynamics1['peak_intensity'], dynamics2['peak_intensity']
        peak_sim = 1 - abs(peak1 - peak2) / (max(peak1, peak2) + 1e-8)
        similarity_score += peak_sim * 0.2
        total_weight += 0.2
        
        return similarity_score / total_weight if total_weight > 0 else 0
    
    def compare_spectral(self, spectral1, spectral2):
        """Compare spectral characteristics"""
        similarity_score = 0
        total_weight = 0

        # Compare spectral centroid (main frequency content)
        centroid1, centroid2 = spectral1['spectral_centroid'], spectral2['spectral_centroid']
        if max(centroid1, centroid2) > 0:
            centroid_sim = 1 - abs(centroid1 - centroid2) / max(centroid1, centroid2)
        else:
            centroid_sim = 1.0 if centroid1 == centroid2 else 0.0
        similarity_score += centroid_sim * 0.4
        total_weight += 0.4

        # Compare spectral spread (frequency distribution width)
        spread1, spread2 = spectral1['spectral_spread'], spectral2['spectral_spread']
        if max(spread1, spread2) > 0:
            spread_sim = 1 - abs(spread1 - spread2) / max(spread1, spread2)
        else:
            spread_sim = 1.0 if spread1 == spread2 else 0.0
        similarity_score += spread_sim * 0.3
        total_weight += 0.3

        # Compare spectral flatness (tonal vs noisy)
        flatness1, flatness2 = spectral1['spectral_flatness'], spectral2['spectral_flatness']
        flatness_sim = 1 - abs(flatness1 - flatness2)
        similarity_score += flatness_sim * 0.3
        total_weight += 0.3
        
        return similarity_score / total_weight if total_weight > 0 else 0
    
    def compare_statistical(self, stats1, stats2):
        """Compare statistical features of the waveform"""
        similarity_score = 0
        total_weight = 0

        # Compare skewness (symmetry of distribution)
        skew1, skew2 = stats1['skewness'], stats2['skewness']
        skew_sim = 1 - min(abs(skew1 - skew2) / 4.0, 1.0)  # Normalize since skewness can be large
        similarity_score += skew_sim * 0.25
        total_weight += 0.25
        
        # Compare kurtosis (tailedness of distribution)
        kurt1, kurt2 = stats1['kurtosis'], stats2['kurtosis']
        kurt_sim = 1 - min(abs(kurt1 - kurt2) / 10.0, 1.0)  # Normalize for kurtosis range
        similarity_score += kurt_sim * 0.25
        total_weight += 0.25
        
        # Compare zero crossing rate (noisiness)
        zcr1, zcr2 = stats1['zero_crossing_rate'], stats2['zero_crossing_rate']
        zcr_sim = 1 - abs(zcr1 - zcr2)
        similarity_score += zcr_sim * 0.25
        total_weight += 0.25

        # Compare autocorrelation features
        autocorr_sim = self.compare_autocorrelation(
            stats1['autocorrelation'], 
            stats2['autocorrelation']
        )
        similarity_score += autocorr_sim * 0.25
        total_weight += 0.25
        
        return similarity_score / total_weight if total_weight > 0 else 0
    
    def compare_autocorrelation(self, autocorr1, autocorr2):
        """Compare autocorrelation patterns"""
        similarity_score = 0
        
        # Compare maximum autocorrelation
        max1, max2 = autocorr1['max_autocorr'], autocorr2['max_autocorr']
        max_sim = 1 - abs(max1 - max2)
        similarity_score += max_sim * 0.5
        
        # Compare autocorrelation peak ratio
        ratio1, ratio2 = autocorr1['autocorr_peak_ratio'], autocorr2['autocorr_peak_ratio']
        if max(ratio1, ratio2) > 0:
            ratio_sim = 1 - abs(ratio1 - ratio2) / max(ratio1, ratio2)
        else:
            ratio_sim = 1.0 if ratio1 == ratio2 else 0.0
        similarity_score += ratio_sim * 0.5
        
        return similarity_score


    
        