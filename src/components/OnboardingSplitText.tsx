import { useEffect, useMemo, useState } from 'react';
import { Animated, StyleSheet, TextStyle, View } from 'react-native';

type Props = {
  text: string;
  style: TextStyle;
  reduceMotion: boolean;
  heading?: boolean;
};

// Native counterpart to the staggered word reveal in React Bits Split Text.
export function OnboardingSplitText({ text, style, reduceMotion, heading = false }: Props) {
  const words = useMemo(() => text.split(/\s+/).filter(Boolean), [text]);
  const values = useMemo(() => words.map(() => new Animated.Value(0)), [words]);
  const [laidOut, setLaidOut] = useState(false);
  const wordSpace = typeof style.fontSize === 'number' ? style.fontSize * 0.24 : 6;
  useEffect(() => {
    values.forEach(value => value.setValue(reduceMotion ? 1 : 0));
    if (reduceMotion || !laidOut) return;
    // Native layout must exist before the per-word motion begins. Otherwise it
    // can finish while the parent screen is still fading into view.
    const animation = Animated.stagger(75, values.map(value => Animated.spring(value, {
      toValue: 1,
      stiffness: 145,
      damping: 17,
      mass: 1,
      isInteraction: false,
      useNativeDriver: true,
    })));
    let frame = 0;
    const start = setTimeout(() => { frame = requestAnimationFrame(() => animation.start()); }, 160);
    return () => { clearTimeout(start); cancelAnimationFrame(frame); animation.stop(); };
  }, [values, reduceMotion, laidOut]);

  return <View accessible accessibilityRole={heading ? 'header' : 'text'} accessibilityLabel={text}
    onLayout={() => setLaidOut(true)} style={styles.line}>
    {words.map((word, index) => <Animated.Text key={index} accessible={false} style={[style, {
      maxWidth: '100%',
      marginRight: index < words.length - 1 ? wordSpace : 0,
      opacity: values[index].interpolate({ inputRange: [0, 1], outputRange: [0, 1], extrapolate: 'clamp' }),
      transform: [{ translateY: reduceMotion ? 0 : values[index].interpolate({ inputRange: [0, 1], outputRange: [22, 0] }) }],
    }]}>{word}</Animated.Text>)}
  </View>;
}

const styles = StyleSheet.create({
  line: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center' },
});
