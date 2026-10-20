import { router } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader } from '../components/AppHeader';
import { AppIcon } from '../components/AppIcon';
import { PeopleSelector } from '../components/PeopleSelector';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';
import { makeStyles } from './profileEditorStyles';
import { cookingStyles } from '../data/cookingStyles';

type Section = 'details' | 'cooking' | 'allergies';
const titles = { details: 'Profile details', cooking: 'Cooking preferences', allergies: 'Allergies & exclusions' };
const commonAllergies = ['Peanuts', 'Shellfish', 'Eggs', 'Dairy', 'Soy', 'Wheat'];
export default function ProfileEditorScreen({ section }: { section: Section }) {
  const { displayName, setDisplayName, diet, setDiet, allergies, setAllergies, exclusions, setExclusions, cookingStyle, setCookingStyle } = useCooking();
  const { palette } = useTheme();
  const styles = makeStyles(palette);
  const [name, setName] = useState(displayName);
  const [other, setOther] = useState('');
  const [excluded, setExcluded] = useState('');
  const back = () => router.canGoBack() ? router.back() : router.replace('/profile');
  function add(value: string, items: string[], setter: (items: string[]) => void, clear: () => void) {
    const cleaned = value.trim().replace(/\s+/g, ' ');
    if (cleaned && !items.some((item) => item.toLowerCase() === cleaned.toLowerCase())) setter([...items, cleaned]);
    clear();
  }
  return <SafeAreaView style={styles.screen}>
    <AppHeader />
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={[styles.row, { justifyContent: 'flex-start' }]}><Pressable accessibilityRole="button" accessibilityLabel="Back to profile" onPress={back} style={styles.settingsButton}><AppIcon name="back" /></Pressable><Text accessibilityRole="header" style={[styles.title, { flex: 1 }]}>{titles[section]}</Text></View>
        {section === 'details' && <><Text style={styles.label}>Name</Text><TextInput accessibilityLabel="Your name" value={name} onChangeText={setName} maxLength={40} autoCapitalize="words" returnKeyType="done" style={styles.nameInput} /></>}
        {section === 'cooking' && <><View style={styles.row}><Text style={styles.label}>Cooking for</Text><PeopleSelector /></View><Text style={styles.label}>Diet</Text><View style={styles.chips}>{(['No preference', 'Vegetarian', 'Halal'] as const).map((value) => <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: diet === value }} onPress={() => setDiet(value)} style={[styles.chip, diet === value && styles.selected]}><Text style={[styles.chipText, diet === value && styles.selectedText]}>{value}</Text></Pressable>)}</View></>}
        {section === 'cooking' && <><Text style={styles.label}>Preferred cooking style</Text><View style={styles.chips}>{cookingStyles.map((value) => <Pressable key={value} accessibilityRole="radio" accessibilityState={{ checked: cookingStyle === value }} onPress={() => setCookingStyle(value)} style={[styles.chip, cookingStyle === value && styles.selected]}><Text style={[styles.chipText, cookingStyle === value && styles.selectedText]}>{value}</Text></Pressable>)}</View></>}
        {section === 'allergies' && <>
          <Text style={styles.section}>Allergies</Text>
          <View style={styles.chips}>{[...new Set([...commonAllergies, ...allergies])].map((value) => <Pressable key={value} accessibilityRole="checkbox" accessibilityState={{ checked: allergies.includes(value) }} onPress={() => setAllergies(allergies.includes(value) ? allergies.filter((item) => item !== value) : [...allergies, value])} style={[styles.chip, allergies.includes(value) && styles.selected]}><Text style={[styles.chipText, allergies.includes(value) && styles.selectedText]}>{value}</Text></Pressable>)}</View>
          <View style={styles.add}><TextInput accessibilityLabel="Other allergy" placeholder="Other allergy" placeholderTextColor={palette.muted} value={other} onChangeText={setOther} maxLength={60} onSubmitEditing={() => add(other, allergies, setAllergies, () => setOther(''))} style={styles.input} /><Pressable accessibilityRole="button" disabled={!other.trim()} onPress={() => add(other, allergies, setAllergies, () => setOther(''))} style={styles.addButton}><Text style={styles.linkText}>Add</Text></Pressable></View>
          <Text style={[styles.section, { marginTop: 28 }]}>Ingredients to avoid</Text>
          <View style={styles.chips}>{exclusions.map((value) => <Pressable key={value} accessibilityRole="button" accessibilityLabel={`Remove ${value} from exclusions`} onPress={() => setExclusions(exclusions.filter((item) => item !== value))} style={styles.chip}><Text style={styles.chipText}>{value} ×</Text></Pressable>)}</View>
          <View style={styles.add}><TextInput accessibilityLabel="Ingredient to avoid" placeholder="Ingredient name" placeholderTextColor={palette.muted} value={excluded} onChangeText={setExcluded} maxLength={60} onSubmitEditing={() => add(excluded, exclusions, setExclusions, () => setExcluded(''))} style={styles.input} /><Pressable accessibilityRole="button" disabled={!excluded.trim()} onPress={() => add(excluded, exclusions, setExclusions, () => setExcluded(''))} style={styles.addButton}><Text style={styles.linkText}>Add</Text></Pressable></View>
        </>}
        <Pressable accessibilityRole="button" disabled={section === 'details' && !name.trim()} onPress={() => { if (section === 'details') setDisplayName(name.trim()); back(); }} style={[styles.done, { marginTop: 28, opacity: section === 'details' && !name.trim() ? 0.5 : 1 }]}><Text style={styles.doneText}>{section === 'details' ? 'Save' : 'Done'}</Text></Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  </SafeAreaView>;
}
