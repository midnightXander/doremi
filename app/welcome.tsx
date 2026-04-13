import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  FlatList,
  TouchableOpacity,
  Animated,
  StatusBar,
  Platform,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width, height } = Dimensions.get('window');

const COLORS = {
  violet: '#6B21A8',
  violetLight: '#8B5CF6',
  violetDark: '#581C87',
  white: '#FFFFFF',
  black: '#1F2937',
  gray: '#6B7280',
  lightGray: '#E5E7EB',
  lighterGray: '#F3F4F6',
};

// 🔴 IMAGES LOCALES - REQUIRE()
const LOGO_SOURCE = require('../assets/images/icon.png');

const ONBOARDING_DATA = [
  {
    id: '1',
    title: 'Ecoute ta musique partout',
    description: 'laisse toi guider par le rythme de tes pas',
    imageSource: require('../assets/images/hehe.jpg'),
  },
  {
    id: '2',
    title: '24h/24 7j/7',
    description: "la musique n'a jamais ete aussi proche de toi",
    imageSource: require('../assets/images/haha.jpg'),
  },
  {
    id: '3',
    title: 'Rejoins nous',
    description: 'rejoins la famille montante des utilisateurs de Doremi',
    imageSource: require('../assets/images/pnj.jpg'),
  },
];

export default function WelcomeScreen() {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showLogo, setShowLogo] = useState(true);
  const flatListRef = useRef<FlatList>(null);

  const fadeAnim = useRef(new Animated.Value(1)).current;
  const slideAnim = useRef(new Animated.Value(0)).current;
  const dotsAnim = useRef(new Animated.Value(0)).current;
  const scaleAnims = useRef(ONBOARDING_DATA.map(() => new Animated.Value(1))).current;

  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(fadeAnim, { toValue: 0, duration: 500, useNativeDriver: true }),
        Animated.timing(slideAnim, { toValue: -height, duration: 500, useNativeDriver: true }),
      ]).start(() => setShowLogo(false));
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    scaleAnims.forEach((anim, index) => {
      Animated.spring(anim, {
        toValue: index === currentIndex ? 1.3 : 1,
        friction: 8,
        tension: 100,
        useNativeDriver: true,
      }).start();
    });
  }, [currentIndex]);

  const handleScroll = (event: any) => {
    const index = Math.round(event.nativeEvent.contentOffset.x / width);
    if (index !== currentIndex) setCurrentIndex(index);
  };

  const completeOnboarding = async () => {
    try {
      await AsyncStorage.setItem('hasSeenOnboarding', 'true');
      router.replace('/homeScreen');
    } catch (error) {
      router.replace('/homeScreen');
    }
  };

  const renderItem = ({ item }: { item: typeof ONBOARDING_DATA[0] }) => (
    <View style={styles.slide}>
      <View style={styles.illustrationContainer}>
        {/* ✅ REQUIRE() ICI */}
        <Image source={item.imageSource} style={styles.illustrationImage} resizeMode="cover" />
      </View>
      <View style={styles.textContainer}>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.description}>{item.description}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.white} />

      {showLogo && (
        <Animated.View style={[styles.logoScreen, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}>
          {/* ✅ REQUIRE() POUR LOGO */}
          <Image source={LOGO_SOURCE} style={styles.logoImage} resizeMode="contain" />
          <View style={styles.loadingBar}>
            <View style={styles.loadingProgress} />
          </View>
        </Animated.View>
      )}

      <FlatList
        ref={flatListRef}
        data={ONBOARDING_DATA}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={handleScroll}
        scrollEventThrottle={16}
      />

      <View style={styles.footer}>
        <View style={styles.dotsContainer}>
          {ONBOARDING_DATA.map((_, index) => (
            <Animated.View
              key={index}
              style={[
                styles.dot,
                index === currentIndex && styles.dotActive,
                { transform: [{ scale: scaleAnims[index] }] },
              ]}
            />
          ))}
        </View>
        <Text style={styles.swipeText}>swipe →</Text>
        {currentIndex === ONBOARDING_DATA.length - 1 && (
          <TouchableOpacity onPress={completeOnboarding} style={styles.startButton}>
            <Text style={styles.startButtonText}>Commencer</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.white },
  logoScreen: { ...StyleSheet.absoluteFillObject, backgroundColor: COLORS.white, justifyContent: 'center', alignItems: 'center', zIndex: 100 },
  logoImage: { width: width * 0.6, height: height * 0.2 },
  loadingBar: { position: 'absolute', bottom: 120, width: 100, height: 3, backgroundColor: COLORS.lightGray, borderRadius: 2, overflow: 'hidden' },
  loadingProgress: { width: '100%', height: '100%', backgroundColor: COLORS.violet },
  slide: { width, flex: 1, backgroundColor: COLORS.white },
  illustrationContainer: { width, height: height * 0.6, paddingTop: Platform.OS === 'ios' ? 50 : 30 },
  illustrationImage: { width, height: '100%', resizeMode: 'cover' },
  textContainer: { flex: 1, paddingHorizontal: 35, paddingTop: 20 },
  title: { fontSize: 30, fontWeight: '800', color: COLORS.black, marginBottom: 12, lineHeight: 38 },
  description: { fontSize: 16, color: COLORS.gray, lineHeight: 24 },
  footer: { paddingBottom: Platform.OS === 'ios' ? 40 : 30, paddingHorizontal: 40, alignItems: 'center', backgroundColor: COLORS.white },
  dotsContainer: { flexDirection: 'row', gap: 12, marginBottom: 25 },
  dot: { width: 10, height: 10, borderRadius: 5, backgroundColor: COLORS.lightGray },
  dotActive: { width: 28, height: 10, borderRadius: 5, backgroundColor: COLORS.violet },
  swipeText: { color: COLORS.gray, fontSize: 13, letterSpacing: 2, textTransform: 'uppercase' },
  startButton: { marginTop: 20, backgroundColor: COLORS.violet, paddingHorizontal: 40, paddingVertical: 16, borderRadius: 30 },
  startButtonText: { color: COLORS.white, fontSize: 17, fontWeight: '700' },
});
