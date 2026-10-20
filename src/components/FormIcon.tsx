import Svg, { Circle, Path, Rect } from 'react-native-svg';
import { useTheme } from '../theme/ThemeContext';

export function FormIcon({ name }: { name: 'email' | 'lock' | 'eye' | 'eye-off' }) {
  const { palette } = useTheme();
  return (
    <Svg width={22} height={22} viewBox="0 0 24 24" fill="none" stroke={palette.muted} strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" accessible={false}>
      {name === 'email' ? <><Rect x="3" y="5" width="18" height="14" rx="3" /><Path d="m4 7 8 6 8-6" /></> :
        name === 'lock' ? <><Rect x="5" y="10" width="14" height="11" rx="3" /><Path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" /></> :
          <><Path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" /><Circle cx="12" cy="12" r="3" />{name === 'eye-off' && <Path d="m3 3 18 18" />}</>}
    </Svg>
  );
}
