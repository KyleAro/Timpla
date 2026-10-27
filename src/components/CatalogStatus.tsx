import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';

export function CatalogStatus() {
  const { catalogLoading, catalogError, reloadCatalog } = useCooking();
  const { palette } = useTheme();
  if (!catalogLoading && !catalogError) return null;
  return <View style={{ paddingVertical: 18, flexDirection: 'row', alignItems: 'center', gap: 12 }}>
    {catalogLoading ? <ActivityIndicator color={palette.accent} accessibilityLabel="Loading recipes" /> : <>
      <Text accessibilityRole="alert" style={{ flex: 1, color: palette.error }}>{catalogError}</Text>
      <Pressable accessibilityRole="button" onPress={reloadCatalog} style={{ minHeight: 44, justifyContent: 'center', paddingHorizontal: 10 }}><Text style={{ color: palette.accent }}>Retry</Text></Pressable>
    </>}
  </View>;
}
