import { Platform } from 'react-native';
import { ScanIngredient } from '../state/scanHistory';

export async function detectIngredients(uri: string, signal: AbortSignal): Promise<ScanIngredient[]> {
  const baseUrl = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '');
  if (!baseUrl) throw new Error('Scanner is not configured.');
  const form = new FormData();
  if (Platform.OS === 'web') {
    const source = await fetch(uri, { signal });
    form.append('image', await source.blob(), 'ingredient-photo.jpg');
  } else {
    const extension = uri.split('?')[0].split('.').pop()?.toLowerCase();
    const mime: Record<string, string> = { png: 'image/png', webp: 'image/webp', heic: 'image/heic', heif: 'image/heif' };
    form.append('image', { uri, name: `ingredient-photo.${extension || 'jpg'}`, type: mime[extension || ''] || 'image/jpeg' } as unknown as Blob);
  }
  let response: Response;
  try { response = await fetch(`${baseUrl}/detect`, { method: 'POST', body: form, signal }); }
  catch { throw new Error('Could not reach the scanner. Check the server and Wi-Fi.'); }
  const payload = await response.json();
  if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : 'Could not scan this photo.');
  if (!Array.isArray(payload.detections)) throw new Error('Invalid scanner response.');
  const found = new Map<string, ScanIngredient>();
  for (const item of payload.detections) {
    if (typeof item.ingredient !== 'string' || !item.ingredient.trim() || typeof item.confidence !== 'number' || !Number.isFinite(item.confidence) || item.confidence < 0 || item.confidence > 1) throw new Error('Invalid scanner response.');
    const raw = item.ingredient.trim();
    const name = raw[0].toUpperCase() + raw.slice(1);
    const previous = found.get(name);
    if (!previous || (previous.confidence ?? 0) < item.confidence) found.set(name, { name, confidence: item.confidence });
  }
  return [...found.values()];
}
