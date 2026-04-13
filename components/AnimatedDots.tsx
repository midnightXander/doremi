import React from 'react';
import { View, Animated, StyleSheet } from 'react-native';
import { Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

interface AnimatedDotsProps {
  data: any[];
  scrollX: Animated.Value;
  currentIndex: number;
}

export default function AnimatedDots({ data, scrollX }: AnimatedDotsProps) {
  return (
    <View style={styles.container}>
      {data.map((_, index) => {
        const inputRange = [
          (index - 1) * width,
          index * width,
          (index + 1) * width,
        ];

        const dotWidth = scrollX.interpolate({
          inputRange,
          outputRange: [10, 30, 10],
          extrapolate: 'clamp',
        });

        const opacity = scrollX.interpolate({
          inputRange,
          outputRange: [0.3, 1, 0.3],
          extrapolate: 'clamp',
        });

        const scale = scrollX.interpolate({
          inputRange,
          outputRange: [1, 1.2, 1],
          extrapolate: 'clamp',
        });

        return (
          <Animated.View
            key={index}
            style={[
              styles.dot,
              {
                width: dotWidth,
                opacity,
                transform: [{ scale }],
              },
            ]}
          />
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  dot: {
    height: 10,
    borderRadius: 5,
    backgroundColor: '#fff',
  },
});
