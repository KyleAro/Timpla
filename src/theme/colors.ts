export const colors = {
  cream: '#FFF8ED',
  red: '#C84B35',
  redPressed: '#AC3C29',
  charcoal: '#302A26',
  muted: '#81766D',
  border: '#DED5CA',
  error: '#A63127',
};

export const themes = {
  light: {
    background: '#FFF8ED', surface: '#FFFCF6', secondary: '#F5EFE5',
    text: '#302A26', muted: '#686057', border: '#8E8275',
    accent: '#B63F2A', accentPressed: '#963321',
    buttonBackground: '#B63F2A', buttonPressed: '#963321',
    olive: '#E5E6D3', oliveText: '#302A26',
    profile: '#E5E6D3', profileText: '#302A26',
    chip: '#F9E5DC', error: '#A63127',
  },
  dark: {
    background: '#1C1B18', surface: '#24231F', secondary: '#292823',
    text: '#FFF8ED', muted: '#C5BEB4', border: '#85796B',
    accent: '#F07B5D', accentPressed: '#F49A80',
    buttonBackground: '#B63F2A', buttonPressed: '#963321',
    olive: '#383E2F', oliveText: '#FFF8ED',
    profile: '#D6D8C1', profileText: '#302A26',
    chip: '#4B3029', error: '#FF8C7C',
  },
} as const;

export type ThemePalette = { [K in keyof typeof themes.light]: string };
