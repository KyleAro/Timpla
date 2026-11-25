import { useReducedMotion } from '../hooks/useReducedMotion';
import { useEffect, useRef, useState } from 'react';
import { typography } from '../theme/tokens';
import { Animated, PanResponder, Pressable, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import type { PropsWithChildren } from 'react';
import { AppIcon } from './AppIcon';

const actionWidth = 88;
export function SwipeDeleteRow({ children, onDelete, label }: PropsWithChildren<{ onDelete: () => void; label: string }>) {
  const { palette } = useTheme();
  const reducedMotion = useReducedMotion();
  const reduced = useRef(true);
  useEffect(() => { reduced.current = reducedMotion; }, [reducedMotion]);
  const [translateX] = useState(() => new Animated.Value(0));
  // The stored gesture callbacks read this ref only in response to touch events.
  // eslint-disable-next-line react-hooks/refs
  const [swipe] = useState(() => {
    const gestureState = { position: 0, start: 0, dragged: false };
    function settle(open: boolean) {
      gestureState.position = open ? -actionWidth : 0;
      if (reduced.current) { translateX.setValue(gestureState.position); return; }
      Animated.spring(translateX, { toValue: gestureState.position, useNativeDriver: true, bounciness: 0 }).start();
    }
    const pan = PanResponder.create({
      onMoveShouldSetPanResponder: (_, gesture) => Math.abs(gesture.dx) > 12 && Math.abs(gesture.dx) > Math.abs(gesture.dy) * 1.5,
      onPanResponderGrant: () => { translateX.stopAnimation(); gestureState.start = gestureState.position; gestureState.dragged = true; },
      onPanResponderMove: (_, gesture) => { translateX.setValue(Math.max(-actionWidth, Math.min(0, gestureState.start + gesture.dx))); },
      onPanResponderRelease: (_, gesture) => { settle(gesture.vx < -0.4 || (gesture.vx <= 0.4 && gestureState.start + gesture.dx < -actionWidth / 2)); setTimeout(() => { gestureState.dragged = false; }, 0); },
      onPanResponderTerminate: () => { settle(gestureState.position < 0); gestureState.dragged = false; },
    });
    return { pan, closeIfOpen() { if (gestureState.position < 0 && !gestureState.dragged) { settle(false); return true; } return false; } };
  });
  return <View style={styles.container}>
    <Pressable accessibilityRole="button" accessibilityLabel={`Delete ${label}`} onPress={onDelete} style={[styles.delete, { backgroundColor: palette.buttonBackground }]}><AppIcon name="trash" size={21} color="#FFF8ED" /><Text style={styles.deleteText}>Delete</Text></Pressable>
    <Animated.View {...swipe.pan.panHandlers} accessibilityActions={[{ name: 'delete', label: `Delete ${label}` }]} onAccessibilityAction={event => { if (event.nativeEvent.actionName === 'delete') onDelete(); }} onStartShouldSetResponderCapture={swipe.closeIfOpen} style={{ transform: [{ translateX }], backgroundColor: palette.background }}>{children}</Animated.View>
  </View>;
}
const styles = StyleSheet.create({
  container: { position: 'relative', borderRadius: 16, overflow: 'hidden', marginBottom: 10 },
  delete: { position: 'absolute', right: 0, top: 0, bottom: 0, width: actionWidth, justifyContent: 'center', alignItems: 'center', gap: 6 }, deleteText: { color: '#FFF8ED', fontWeight: '700', fontSize: typography.label },
});
