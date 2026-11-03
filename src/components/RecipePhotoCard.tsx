import { router } from 'expo-router';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { recipeImage } from '../utils/recipeImages';
import { useTheme } from '../theme/ThemeContext';
import { AppIcon } from './AppIcon';
import { SaveRecipeButton } from './SaveRecipeButton';

type Dish = { id: string; name: string; versions: { family: string }[] };
export function RecipePhotoCard({ dish, featured = false }: { dish: Dish; featured?: boolean }) {
  const { palette } = useTheme();
  return <View style={[styles.card, { backgroundColor: palette.surface, borderColor: palette.border }, featured && styles.featured]}>
    <Pressable accessibilityRole="button" accessibilityLabel={`Open ${dish.name}`} onPress={() => router.push({ pathname: '/recipe', params: { id: dish.id } })} style={({ pressed }) => [styles.link, { opacity: pressed ? .88 : 1 }]}>
      <Image source={recipeImage(dish.versions[0].family)} accessibilityLabel={`${dish.name} illustration`} style={[styles.photo, featured && styles.featuredPhoto]} />
      <View style={[styles.caption, !featured && styles.gridCaption]}>
        {featured && <View style={[styles.badge, { backgroundColor: palette.olive }]}><Text style={{ color: palette.oliveText, fontSize: 12, fontWeight: '600' }}>A little kitchen inspiration</Text></View>}
        <View style={styles.bottom}><View style={styles.copy}><Text numberOfLines={2} ellipsizeMode="tail" style={[styles.name, featured ? styles.featuredName : styles.gridTitle]}>{dish.name}</Text><Text numberOfLines={1} style={styles.options}>{dish.versions.length} recipe {dish.versions.length === 1 ? 'option' : 'options'}</Text></View><View style={styles.arrow}><AppIcon name="chevron" color="#302A26" size={18} /></View></View>
      </View>
    </Pressable>
    <SaveRecipeButton id={dish.id} floating />
  </View>;
}
const styles = StyleSheet.create({
  card: { flex: 1, minWidth: 0, borderRadius: 20, overflow: 'hidden', borderWidth: StyleSheet.hairlineWidth }, featured: { marginBottom: 22 },
  link: { flex: 1, minHeight: 215 }, photo: { width: '100%', height: 235, resizeMode: 'cover' }, featuredPhoto: { height: 285 },
  caption: { position: 'absolute', left: 0, right: 0, bottom: 0, padding: 13, paddingTop: 12, backgroundColor: 'rgba(32,25,20,0.78)', gap: 10 },
  gridCaption: { height: 100, justifyContent: 'center' }, copy: { flex: 1, minWidth: 0 }, gridTitle: { height: 42, lineHeight: 21 },
  badge: { alignSelf: 'flex-start', borderRadius: 18, paddingHorizontal: 11, paddingVertical: 6 },
  bottom: { flexDirection: 'row', alignItems: 'center', gap: 6 }, name: { fontSize: 16, lineHeight: 21, color: '#FFF8ED', fontWeight: '700' }, featuredName: { fontSize: 26, lineHeight: 31 },
  options: { color: '#F8EDE2', fontSize: 12, lineHeight: 17, marginTop: 5 }, arrow: { flexShrink: 0, width: 30, height: 30, borderRadius: 15, backgroundColor: '#FFF8ED', alignItems: 'center', justifyContent: 'center' },
});
