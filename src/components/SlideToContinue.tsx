import { typography } from '../theme/tokens';
import { useEffect, useMemo, useRef, useState } from 'react';
import { AccessibilityInfo, Animated, PanResponder, Platform, Pressable, StyleSheet, Text } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

type Props = { label: string; disabled?: boolean; onComplete: () => void; reduceMotion: boolean };

export function SlideToContinue({ label, disabled = false, onComplete, reduceMotion }: Props) {
  const { palette } = useTheme();
  const [width, setWidth] = useState(0);
  const [offset] = useState(() => new Animated.Value(0));
  const [screenReader, setScreenReader] = useState(false);
  const completed = useRef(false);
  const travel = Math.max(0, width - 60);

  useEffect(() => {
    let active = true;
    void AccessibilityInfo.isScreenReaderEnabled().then(enabled => { if (active) setScreenReader(enabled); }).catch(() => {});
    const subscription = AccessibilityInfo.addEventListener('screenReaderChanged', setScreenReader);
    return () => { active = false; subscription.remove(); };
  }, []);
  useEffect(() => {
    if (!disabled) { completed.current = false; offset.setValue(0); }
  }, [disabled, offset]);

  const responder = useMemo(() => {
    function complete() {
      if (completed.current || disabled) return;
      completed.current = true;
      onComplete();
    }
    function reset() {
      Animated.timing(offset, { toValue: 0, duration: reduceMotion ? 0 : 220, useNativeDriver: false }).start();
    }
    // PanResponder stores these handlers; the completion ref is read only when a gesture ends.
    // eslint-disable-next-line react-hooks/refs
    return PanResponder.create({
      onStartShouldSetPanResponder: () => !disabled && !screenReader && travel > 0,
      onMoveShouldSetPanResponder: (_, gesture) => !disabled && !screenReader && Math.abs(gesture.dx) > Math.abs(gesture.dy),
      onPanResponderGrant: () => offset.stopAnimation(),
      onPanResponderMove: (_, gesture) => offset.setValue(Math.max(0, Math.min(travel, gesture.dx))),
      onPanResponderRelease: (_, gesture) => {
        if (travel > 0 && gesture.dx >= travel * 0.85) {
          offset.setValue(travel);
          complete();
        } else reset();
      },
      onPanResponderTerminationRequest: () => true,
      onPanResponderTerminate: reset,
    });
  }, [disabled, screenReader, travel, offset, onComplete, reduceMotion]);

  function accessibleComplete() {
    if (disabled || completed.current) return;
    completed.current = true;
    onComplete();
  }

  return <Pressable
    accessible
    accessibilityRole="button"
    accessibilityLabel={label}
    accessibilityHint="Slide the arrow to the right, or double tap with a screen reader, to continue."
    accessibilityState={{ disabled }}
    onAccessibilityTap={accessibleComplete}
    onPress={() => { if (screenReader || Platform.OS === 'web') accessibleComplete(); }}
    disabled={disabled}
    onLayout={event => setWidth(event.nativeEvent.layout.width)}
    style={[styles.track, { backgroundColor: palette.surface, borderColor: palette.border, opacity: disabled ? 0.5 : 1 }]}
  >
    <Text style={[styles.label, { color: palette.text }]}>{label}</Text>
    <Animated.View {...responder.panHandlers} accessible={false} style={[styles.thumb, { backgroundColor: palette.buttonBackground, transform: [{ translateX: offset }] }]}>
      <Text style={styles.arrow}>›</Text>
    </Animated.View>
  </Pressable>;
}

const styles = StyleSheet.create({
  track: { minHeight: 60, justifyContent: 'center', borderWidth: 1, borderRadius: 30, paddingHorizontal: 60, paddingVertical: 16 },
  label: { fontSize: typography.body, fontWeight: '600', textAlign: 'center' },
  thumb: { position: 'absolute', left: 5, top: 5, bottom: 5, width: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  arrow: { color: '#fff8ed', fontSize: 34, lineHeight: 38 },
});
