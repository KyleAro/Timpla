import Svg, { Circle, Path, Rect } from 'react-native-svg';
import { useTheme } from '../theme/ThemeContext';

export type IconName = 'bookmark' | 'camera' | 'upload' | 'plus' | 'people' | 'sliders' | 'home' | 'book' | 'user' | 'back' | 'trash' | 'leaf' | 'sun' | 'moon' | 'chevron' | 'edit' | 'settings' | 'check' | 'reverse' | 'history' | 'help' | 'flash' | 'flash-off' | 'close';
export function AppIcon({ name, size = 24, color }: { name: IconName; size?: number; color?: string }) {
  const { palette } = useTheme();
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color ?? palette.text} strokeWidth={1.65} strokeLinecap="round" strokeLinejoin="round" accessible={false}>
      {name === 'camera' && <><Path d="M4 7h3l2-3h6l2 3h3a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1Z" /><Circle cx="12" cy="13" r="4" /></>}
      {name === 'upload' && <><Rect x="3" y="3" width="18" height="18" rx="3" /><Circle cx="8" cy="8" r="1.5" /><Path d="m3 17 6-6 4 4 3-3 5 5" /></>}
      {name === 'plus' && <Path d="M12 4v16M4 12h16" />}
      {name === 'bookmark' && <Path d="M6 3h12v18l-6-4-6 4V3Z" />}
      {name === 'people' && <><Circle cx="9" cy="7" r="3" /><Path d="M3 21v-3a6 6 0 0 1 12 0v3H3ZM17 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3" /></>}
      {name === 'sliders' && <><Path d="M3 6h5m4 0h9M3 12h11m4 0h3M3 18h3m4 0h11" /><Circle cx="10" cy="6" r="2" /><Circle cx="16" cy="12" r="2" /><Circle cx="8" cy="18" r="2" /></>}
      {name === 'home' && <Path d="m3 10 9-7 9 7v10H15v-6H9v6H3V10Z" />}
      {name === 'book' && <><Path d="M12 5v16M3 4c4-1 7 0 9 1 2-1 5-2 9-1v15c-4-1-7 0-9 2-2-2-5-3-9-2V4Z" /></>}
      {name === 'user' && <><Circle cx="12" cy="7" r="4" /><Path d="M4 21v-2a8 8 0 0 1 16 0v2" /></>}
      {name === 'back' && <Path d="m14 5-7 7 7 7" />}
      {name === 'trash' && <><Path d="M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7" /></>}
      {name === 'leaf' && <><Path d="M20 3C12 3 5 7 5 15a6 6 0 0 0 6 6c8 0 10-10 9-18Z" /><Path d="M4 22c3-7 7-10 13-14" /></>}
      {name === 'sun' && <><Circle cx="12" cy="12" r="4" /><Path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>}
      {name === 'moon' && <Path d="M20 16.2A8.5 8.5 0 0 1 7.8 4 8.5 8.5 0 1 0 20 16.2Z" />}
      {name === 'chevron' && <Path d="m9 5 7 7-7 7" />}
      {name === 'edit' && <><Path d="m4 17 11-11 3 3L7 20l-4 1 1-4ZM14 7l3-3a2 2 0 0 1 3 3l-3 3" /></>}
      {name === 'settings' && <><Circle cx="12" cy="12" r="3" /><Path d="M10 2h4l.6 2.2 1.8.8 2-.9 2.8 2.8-.9 2 .8 1.8L23 11v2l-2.2.6-.8 1.8.9 2-2.8 2.8-2-.9-1.8.8L14 22h-4l-.6-2.2-1.8-.8-2 .9-2.8-2.8.9-2-.8-1.8L1 13v-2l2.2-.6.8-1.8-.9-2L5.9 3.8l2 .9 1.8-.8L10 2Z" /></>}
      {name === 'close' && <Path d="m6 6 12 12M18 6 6 18" />}
      {name === 'check' && <Path d="m4 12 5 5L20 6" />}
      {(name === 'flash' || name === 'flash-off') && <><Path d="m13 2-8 12h6l-1 8 9-13h-6l1-7Z" />{name === 'flash-off' && <Path d="m3 3 18 18" />}</>}
      {name === 'help' && <><Circle cx="12" cy="12" r="9" /><Path d="M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1-1.5 2M12 16h.01" /></>}
      {name === 'history' && <><Path d="M3 11a9 9 0 1 1 2.6 7M3 4v7h7M12 7v5l3 2" /></>}
      {name === 'reverse' && <><Path d="M8 5H5l3-3M5 5h9a7 7 0 0 1 7 7M3 13h14M5 13v7h10v-7M8 10h4" /></>}
    </Svg>
  );
}
