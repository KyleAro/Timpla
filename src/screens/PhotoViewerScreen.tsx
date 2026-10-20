import { router } from 'expo-router';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppIcon } from '../components/AppIcon';
import { useCooking } from '../state/CookingContext';

export default function PhotoViewerScreen() {
  const { photo } = useCooking();
  return <View style={styles.screen}>
    {photo ? <Image source={{ uri: photo }} accessibilityLabel="Captured ingredient photo" resizeMode="contain" style={StyleSheet.absoluteFill} /> : <Text style={styles.empty}>Photo unavailable</Text>}
    <SafeAreaView pointerEvents="box-none" style={styles.overlay}>
      <Pressable accessibilityRole="button" accessibilityLabel="Close photo" onPress={() => router.canGoBack() ? router.back() : router.replace('/ingredients')} style={styles.close}><AppIcon name="close" size={27} color="#FFFFFF" /></Pressable>
    </SafeAreaView>
  </View>;
}
const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000000', alignItems: 'center', justifyContent: 'center' },
  overlay: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0, alignItems: 'flex-start', paddingHorizontal: 12 },
  close: { width: 48, height: 48, borderRadius: 24, backgroundColor: '#00000099', alignItems: 'center', justifyContent: 'center', marginTop: 12 },
  empty: { color: '#FFFFFF', fontSize: 16 },
});
