import { useCallback, RefObject } from 'react';
import { AccessibilityInfo, findNodeHandle, Platform, Text } from 'react-native';

export function useDialogFocus(titleRef: RefObject<Text | null>) {
  const onShow = useCallback(() => {
    requestAnimationFrame(() => {
      const title = titleRef.current;
      if (!title) return;
      if (Platform.OS === 'web') {
        const element = title as unknown as { focus?: () => void; setAttribute?: (name: string, value: string) => void };
        element.setAttribute?.('tabindex', '-1');
        element.focus?.();
      } else {
        const handle = findNodeHandle(title);
        if (handle !== null) AccessibilityInfo.setAccessibilityFocus(handle);
      }
    });
  }, [titleRef]);
  return onShow;
}
