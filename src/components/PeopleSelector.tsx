import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useCooking } from '../state/CookingContext';
import { colors } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';
import { useState } from 'react';

export function PeopleSelector({ value, onChange }: { value?: number; onChange?: (value: number) => void } = {}) {
  const { people: savedPeople, savePreferences } = useCooking();
  const people = value ?? savedPeople;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const { palette } = useTheme();
  async function change(next: number) {
    if (onChange) { onChange(next); return; }
    setBusy(true); setError('');
    try { await savePreferences({ people: next }); }
    catch { setError('Could not save servings.'); }
    finally { setBusy(false); }
  }
  return (
    <View>
    <View style={[styles.container, { borderColor: palette.border }]}>
      <AppIcon name="people" size={20} />
      <Pressable accessibilityRole="button" accessibilityLabel="Cook for one fewer person" disabled={busy || people === 1} onPress={() => { void change(people - 1); }} style={[styles.control, (busy || people === 1) && styles.disabled]}><Text style={[styles.symbol, { color: palette.text }]}>−</Text></Pressable>
      <Text accessibilityLabel={`Cooking for ${people} ${people === 1 ? 'person' : 'people'}`} accessibilityLiveRegion="polite" style={[styles.count, { color: palette.text }]}>{people}</Text>
      <Pressable accessibilityRole="button" accessibilityLabel="Cook for one more person" disabled={busy || people === 20} onPress={() => { void change(people + 1); }} style={[styles.control, (busy || people === 20) && styles.disabled]}><Text style={[styles.symbol, { color: palette.text }]}>+</Text></Pressable>
    </View>
    {error ? <Text accessibilityRole="alert" style={{ color: palette.error, fontSize: 12, marginTop: 6 }}>{error}</Text> : null}
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
