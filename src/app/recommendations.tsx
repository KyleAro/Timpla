import { router } from 'expo-router';
import { Pressable, ScrollView, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { RecipeMatchesPreview } from '../components/RecipeMatchesPreview';
import { useTheme } from '../theme/ThemeContext';

export default function Recommendations() {
  const { palette } = useTheme();
  return <SafeAreaView style={{ flex: 1, backgroundColor: palette.background }}>
    <ScrollView contentContainerStyle={{ padding: 20 }}>
      <Pressable accessibilityRole="button" onPress={() => router.canGoBack() ? router.back() : router.replace('/home')} style={{ minHeight: 44, justifyContent: 'center' }}><Text style={{ color: palette.accent }}>Back</Text></Pressable>
      <RecipeMatchesPreview expanded />
    </ScrollView>
  </SafeAreaView>;
}
