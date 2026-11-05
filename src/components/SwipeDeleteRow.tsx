import { useMemo, useRef } from 'react';
import { Animated, PanResponder, Pressable, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import type { PropsWithChildren } from 'react';
import { AppIcon } from './AppIcon';

const actionWidth = 88;
export function SwipeDeleteRow({ children, onDelete, label }: PropsWithChildren<{ onDelete: () => void; label: string }>) {
  const { palette } = useTheme();
  const translateX = useRef(new Animated.Value(0)).current;
  const position = useRef(0);
  const start = useRef(0);
  const dragged = useRef(false);
  const pan = useMemo(() => {
    function settle(open: boolean) {
      position.current = open ? -actionWidth : 0;
      Animated.spring(translateX, { toValue: position.current, useNativeDriver: true, bounciness: 0 }).start();
    }
    return PanResponder.create({
      onMoveShouldSetPanResponder: (_, gesture) => Math.abs(gesture.dx) > 12 && Math.abs(gesture.dx) > Math.abs(gesture.dy) * 1.5,
      onPanResponderGrant: () => { translateX.stopAnimation(); start.current = position.current; dragged.current = true; },
      onPanResponderMove: (_, gesture) => { translateX.setValue(Math.max(-actionWidth, Math.min(0, start.current + gesture.dx))); },
      onPanResponderRelease: (_, gesture) => { settle(gesture.vx < -0.4 || (gesture.vx <= 0.4 && start.current + gesture.dx < -actionWidth / 2)); setTimeout(() => { dragged.current = false; }, 0); },
      onPanResponderTerminate: () => { settle(position.current < 0); dragged.current = false; },
    });
  }, [translateX]);
  return <View style={styles.container}>
    <Pressable accessibilityRole="button" accessibilityLabel={`Delete ${label}`} onPress={onDelete} style={[styles.delete, { backgroundColor: palette.accent }]}><AppIcon name="trash" size={21} color="#FFF8ED" /><Text style={styles.deleteText}>Delete</Text></Pressable>
    <Animated.View {...pan.panHandlers} accessibilityActions={[{ name: 'delete', label: `Delete ${label}` }]} onAccessibilityAction={event => { if (event.nativeEvent.actionName === 'delete') onDelete(); }} onStartShouldSetResponderCapture={() => { if (position.current < 0 && !dragged.current) { position.current = 0; Animated.spring(translateX, { toValue: 0, useNativeDriver: true }).start(); return true; } return false; }} style={{ transform: [{ translateX }], backgroundColor: palette.background }}>{children}</Animated.View>
  </View>;
}
const styles = StyleSheet.create({
  container: { position: 'relative', borderRadius: 16, overflow: 'hidden', marginBottom: 10 },
  delete: { position: 'absolute', right: 0, top: 0, bottom: 0, width: actionWidth, justifyContent: 'center', alignItems: 'center', gap: 6 }, deleteText: { color: '#FFF8ED', fontWeight: '700', fontSize: 13 },
});
