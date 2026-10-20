import { Image } from 'react-native';
import { useTheme } from '../theme/ThemeContext';

// One transparent silhouette; only its color changes with the app theme.
export function BrandMark({ size = 112, color }: { size?: number; color?: string }) {
  const { mode, palette } = useTheme();
  return <Image source={require('../../assets/brand/timpla-mark-transparent.png')} accessibilityLabel="Timpla bowl and spoon logo" style={{ width: size, height: size, resizeMode: 'contain', tintColor: color ?? (mode === 'dark' ? '#FFFFFF' : palette.accent) }} />;
}

