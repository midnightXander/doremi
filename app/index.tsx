import { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function Index() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      // Petit délai pour éviter le flash
      await new Promise(resolve => setTimeout(resolve, 1000));

      const hasSeenOnboarding = await AsyncStorage.getItem('hasSeenOnboarding');

      if (hasSeenOnboarding === 'true') {
        router.replace('/homeScreen');
      } else {
        router.replace('/welcome');
      }
    } catch (error) {
      console.error('Erreur:', error);
      router.replace('/welcome');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#1a1a2e' }}>
        <ActivityIndicator size="large" color="#667eea" />
      </View>
    );
  }

  return null;
}
