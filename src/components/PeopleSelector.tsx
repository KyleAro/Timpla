import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useCooking } from '../state/CookingContext';
import { colors } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';

export function PeopleSelector() {
  const { people, setPeople } = useCooking();
  const { palette } = useTheme();
  return (
    <View style={[styles.container, { borderColor: palette.border }]}>
      <AppIcon name="people" size={20} />
      <Pressable accessibilityRole="button" accessibilityLabel="Cook for one fewer person" disabled={people === 1} onPress={() => setPeople(people - 1)} style={[styles.control, people === 1 && styles.disabled]}><Text style={[styles.symbol, { color: palette.text }]}>−</Text></Pressable>
      <Text accessibilityLabel={`Cooking for ${people} ${people === 1 ? 'person' : 'people'}`} accessibilityLiveRegion="polite" style={[styles.count, { color: palette.text }]}>{people}</Text>
      <Pressable accessibilityRole="button" accessibilityLabel="Cook for one more person" disabled={people === 20} onPress={() => setPeople(people + 1)} style={[styles.control, people === 20 && styles.disabled]}><Text style={[styles.symbol, { color: palette.text }]}>+</Text></Pressable>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', paddingLeft: 12, borderColor: colors.border, borderWidth: 1, borderRadius: 28, minHeight: 50 },
  control: { minWidth: 44, minHeight: 48, alignItems: 'center', justifyContent: 'center' },
  disabled: { opacity: 0.3 },
  count: { fontSize: 17, fontWeight: '600', minWidth: 22, textAlign: 'center', color: colors.charcoal },
  symbol: { fontSize: 24, color: colors.charcoal },
});
