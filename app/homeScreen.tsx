import React from 'react';
import { View, Text } from 'react-native';


export default function HomeScreen() {
  /*const router = useRouter();

  const resetOnboarding = async () => {
    await AsyncStorage.removeItem('hasSeenOnboarding');
    router.replace('/welcome');
  };*/

  return (
    <View
      style={{
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
      }}>
      <Text>home</Text>
    </View>
  );
}

