import { Platform } from 'react-native';
import { File } from 'expo-file-system';
import { fetch as expoFetch } from 'expo/fetch';
import type { ScanDetection, ScanIngredient } from '../state/scanHistory';
import { detectOffline, prepareOfflineDetector, supportsOfflineDetection } from './offlineDetection';

export type DetectionResult = {
  ingredients: ScanIngredient[];
  detections: ScanDetection[];
  width?: number;
  height?: number;
};

export function getDetectorBaseUrl() {
  if (process.env.EXPO_PUBLIC_DETECTOR_ENABLED === 'false') return undefined;
  const configuredUrl = process.env.EXPO_PUBLIC_DETECTOR_URL?.trim().replace(/\/$/, '');
  // In web development, route through Metro so browser and phone uploads share
  // the local detector proxy. Native builds use the configured detector URL.
  const baseUrl = typeof __DEV__ !== 'undefined' && __DEV__ && Platform.OS === 'web' && typeof window !== 'undefined'
    ? `${window.location.origin}/timpla-detector`
    : configuredUrl;
  return baseUrl;
}

export type DetectorServiceStatus = 'active' | 'idle';

export async function checkDetectorStatus(signal: AbortSignal): Promise<DetectorServiceStatus> {
  if (supportsOfflineDetection()) {
    try {
      await prepareOfflineDetector();
      if (signal.aborted) throw new Error('Scan cancelled.');
      return 'idle';
    } catch (error) {
      if (!getDetectorBaseUrl()) throw error;
    }
  }
  const baseUrl = getDetectorBaseUrl();
  if (!baseUrl) throw new Error('Scanner address is not configured.');
  // /health is already allowed by the existing local Metro proxy and also
  // returns the detector's active/idle state.
  const response = await fetch(`${baseUrl}/health`, { signal });
  if (!response.ok) throw new Error(`Scanner returned HTTP ${response.status}.`);
  const payload = await response.json() as { ready?: unknown; status?: unknown };
  if (payload?.ready !== true) throw new Error('Scanner is responding but not ready yet.');
  return payload.status === 'active' ? 'active' : 'idle';
}

export async function detectIngredients(uri: string, signal: AbortSignal): Promise<DetectionResult> {
  if (supportsOfflineDetection()) {
    try { return await detectOffline(uri, signal); }
    catch (error) {
      if (signal.aborted || !getDetectorBaseUrl()) throw error;
    }
  }
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
    throw new Error(`Scanner upload failed: ${reason}. Check your network connection and detector service status.`);
  }
  const rawResponse = await response.text();
  let payload: { detail?: unknown; ingredients?: unknown; detections?: unknown; width?: unknown; height?: unknown };
  try { payload = JSON.parse(rawResponse) as typeof payload; }
  catch {
    const excerpt = rawResponse.replace(/\s+/g, ' ').trim().slice(0, 240) || '(empty response body)';
    throw new Error(`Scanner returned non-JSON HTTP ${response.status}${response.statusText ? ` ${response.statusText}` : ''}: ${excerpt}`);
  }
  if (!payload || typeof payload !== 'object') throw new Error('The detector returned an invalid response.');
  if (!response.ok) {
    const detail = typeof payload.detail === 'string' ? payload.detail : 'Could not detect ingredients in this photo.';
    throw new Error(`Scanner returned HTTP ${response.status}: ${detail}`);
  }
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
  const detections: ScanDetection[] = [];
  if (Array.isArray(payload.detections)) {
    for (const value of payload.detections) {
      if (!value || typeof value !== 'object') continue;
      const item = value as {
        name?: unknown;
        label?: unknown;
        confidence?: unknown;
        bbox_xyxy?: unknown;
        source_model?: unknown;
      };
      if (
        typeof item.name !== 'string' || !item.name.trim() ||
        typeof item.label !== 'string' || !item.label.trim() ||
        typeof item.confidence !== 'number' || !Number.isFinite(item.confidence) ||
        !Array.isArray(item.bbox_xyxy) || item.bbox_xyxy.length !== 4 ||
        !item.bbox_xyxy.every((coordinate) => typeof coordinate === 'number' && Number.isFinite(coordinate))
      ) continue;
      const [x1, y1, x2, y2] = item.bbox_xyxy as number[];
      if (x2 <= x1 || y2 <= y1) continue;
      detections.push({
        name: item.name.trim(),
        label: item.label.trim(),
        confidence: item.confidence,
        bbox_xyxy: [x1, y1, x2, y2],
        ...(typeof item.source_model === 'string' ? { source_model: item.source_model } : {}),
      });
    }
  }
  return {
    ingredients: [...found.values()],
    detections,
    width: typeof payload.width === 'number' && Number.isFinite(payload.width) && payload.width > 0 ? payload.width : undefined,
    height: typeof payload.height === 'number' && Number.isFinite(payload.height) && payload.height > 0 ? payload.height : undefined,
  };
}
