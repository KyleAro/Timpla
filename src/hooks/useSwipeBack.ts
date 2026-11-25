import { useMemo } from 'react';
import { PanResponder, Platform, useWindowDimensions } from 'react-native';

export function useSwipeBack(enabled: boolean, onBack: () => void) {
  const { width } = useWindowDimensions();
  const mobile = Platform.OS === 'ios' || Platform.OS === 'android';

  return useMemo(() => {
    if (!mobile || !enabled) return {};

    const isLeftSwipe = (dx: number, dy: number, distance: number) =>
      dx <= -distance && -dx > Math.abs(dy) * 1.5;

    return PanResponder.create({
      onMoveShouldSetPanResponderCapture: (event, gesture) => {
        const rightInset = width - (event.nativeEvent.pageX - gesture.dx);
        return gesture.numberActiveTouches === 1
          && rightInset >= 24 && rightInset <= 64
          && isLeftSwipe(gesture.dx, gesture.dy, 18);
      },
      onPanResponderRelease: (_, gesture) => {
        if (isLeftSwipe(gesture.dx, gesture.dy, 64)) onBack();
      },
    }).panHandlers;
  }, [enabled, mobile, onBack, width]);
}
