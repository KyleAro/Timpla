import { Platform } from 'react-native';
import { File } from 'expo-file-system';
import { fetch as expoFetch } from 'expo/fetch';
import type { ScanIngredient } from '../state/scanHistory';

export function getDetectorBaseUrl() {
  const configuredUrl = process.env.EXPO_PUBLIC_DETECTOR_URL?.trim().replace(/\/$/, '');
  // Browser development uses the page's origin to avoid cross-origin LAN
  // restrictions. Expo Go uses the configured LAN URL on the same Metro port.
  const baseUrl = typeof __DEV__ !== 'undefined' && __DEV__ && Platform.OS === 'web' && typeof window !== 'undefined'
    ? `${window.location.origin}/timpla-detector`
    : configuredUrl;
  return baseUrl;
}

export async function detectIngredients(uri: string, signal: AbortSignal): Promise<ScanIngredient[]> {
  const baseUrl = getDetectorBaseUrl();
  if (!baseUrl) throw new Error('Ingredient detector is not configured. Add ingredients manually or set the detector address.');
  const form = new FormData();
  if (Platform.OS === 'web') {
    const response = await fetch(uri, { signal });
    if (!response.ok) throw new Error('Could not read the selected photo.');
    form.append('image', await response.blob(), 'ingredient-photo.jpg');
  } else {
    const file = new File(uri);
    if (!file.exists || file.size <= 0) throw new Error('This photo is no longer available. Select it again.');
    // SDK 57 defaults to Expo fetch. A plain {uri,name,type} part has no
    // bytes() method and fails before any request reaches the detector.
    form.append('image', file);
  }
  let response: Response;
  try {
    const upload = Platform.OS === 'web' ? fetch : expoFetch;
    response = await upload(`${baseUrl}/detect`, { method: 'POST', body: form, signal });
  }
  catch (error) {
    if (signal.aborted) throw error;
    const reason = error instanceof Error ? error.message : 'Unknown upload error';
    throw new Error(`Scanner upload failed: ${reason}. Check Expo Go's Local Network access and that Expo is running on your PC.`);
  }
  let payload: { detail?: unknown; ingredients?: unknown };
  try { payload = await response.json(); }
  catch { throw new Error('The detector returned an unreadable response. Try again.'); }
  if (!payload || typeof payload !== 'object') throw new Error('The detector returned an invalid response.');
  if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : 'Could not detect ingredients in this photo.');
  if (!Array.isArray(payload.ingredients)) throw new Error('The detector returned an invalid ingredient list.');
  const found = new Map<string, ScanIngredient>();
  for (const value of payload.ingredients) {
    if (!value || typeof value !== 'object') throw new Error('The detector returned an invalid ingredient.');
    const item = value as { label?: unknown; name?: unknown; confidence?: unknown };
    if (typeof item.name !== 'string' || !item.name.trim() || typeof item.label !== 'string' || !item.label.trim() || typeof item.confidence !== 'number' || !Number.isFinite(item.confidence) || item.confidence < 0 || item.confidence > 1) throw new Error('The detector returned an invalid ingredient.');
    const clean = item.name.trim();
    const name = clean[0].toUpperCase() + clean.slice(1);
    const key = name.toLowerCase();
    const previous = found.get(key);
    if (!previous || (previous.confidence ?? 0) < item.confidence) found.set(key, { name, confidence: item.confidence, label: item.label });
  }
  return [...found.values()];
}
