import { Asset } from 'expo-asset';
import { isRunningInExpoGo } from 'expo';
import { File } from 'expo-file-system';
import { ImageManipulator, SaveFormat } from 'expo-image-manipulator';
import { Image, Platform } from 'react-native';
import { decode } from 'jpeg-js';
import labels from '../data/offlineDetectorLabels.json';
import type { DetectionResult } from './detection';

const SIZE = 512;
const CHANNEL_PIXELS = SIZE * SIZE;
// Metro exposes binary ONNX files as assets through a static require.
// eslint-disable-next-line @typescript-eslint/no-require-imports
const MODEL = require('../../assets/models/ingredients_68.onnx');
const ALIASES: Record<string, string> = { sili: 'chili' };

type Runtime = typeof import('onnxruntime-react-native');
type Session = Awaited<ReturnType<Runtime['InferenceSession']['create']>>;
let sessionPromise: Promise<{ runtime: Runtime; session: Session }> | undefined;

export function supportsOfflineDetection() {
  return Platform.OS === 'android' && !isRunningInExpoGo();
}

export async function prepareOfflineDetector() {
  if (!supportsOfflineDetection()) throw new Error('Offline detection is available in the Android app build.');
  sessionPromise ??= (async () => {
    const asset = Asset.fromModule(MODEL);
    await asset.downloadAsync();
    if (!asset.localUri) throw new Error('The bundled detector model is unavailable.');
    const runtime = await import('onnxruntime-react-native');
    const bytes = await new File(asset.localUri).bytes();
    const session = await runtime.InferenceSession.create(bytes, { executionProviders: ['cpu'] });
    return { runtime, session };
  })().catch(error => { sessionPromise = undefined; throw error; });
  return sessionPromise;
}

function imageSize(uri: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => Image.getSize(uri, (width, height) => resolve({ width, height }), reject));
}

function clamp(value: number, maximum: number) {
  return Math.max(0, Math.min(maximum, value));
}

export async function detectOffline(uri: string, signal: AbortSignal): Promise<DetectionResult> {
  if (signal.aborted) throw new Error('Scan cancelled.');
  const [{ runtime, session }, original] = await Promise.all([prepareOfflineDetector(), imageSize(uri)]);
  const scale = Math.min(SIZE / original.width, SIZE / original.height);
  const resizedWidth = Math.max(1, Math.round(original.width * scale));
  const resizedHeight = Math.max(1, Math.round(original.height * scale));
  const padX = Math.floor((SIZE - resizedWidth) / 2);
  const padY = Math.floor((SIZE - resizedHeight) / 2);
  const context = ImageManipulator.manipulate(uri);
  let jpeg: Uint8Array;
  try {
    context.resize({ width: resizedWidth, height: resizedHeight });
    const rendered = await context.renderAsync();
    try {
      const photo = await rendered.saveAsync({ format: SaveFormat.JPEG, compress: 0.95 });
      jpeg = await new File(photo.uri).bytes();
    } finally { rendered.release(); }
  } finally { context.release(); }
  if (signal.aborted) throw new Error('Scan cancelled.');
  const decoded = decode(jpeg, { useTArray: true, formatAsRGBA: true });
  if (decoded.width !== resizedWidth || decoded.height !== resizedHeight) throw new Error('Could not prepare the photo for offline scanning.');
  const input = new Float32Array(3 * CHANNEL_PIXELS);
  input.fill(114 / 255);
  for (let y = 0; y < resizedHeight; y++) {
    for (let x = 0; x < resizedWidth; x++) {
      const source = (y * resizedWidth + x) * 4;
      const target = (y + padY) * SIZE + x + padX;
      input[target] = decoded.data[source] / 255;
      input[CHANNEL_PIXELS + target] = decoded.data[source + 1] / 255;
      input[2 * CHANNEL_PIXELS + target] = decoded.data[source + 2] / 255;
    }
  }
  const output = await session.run({ [session.inputNames[0]]: new runtime.Tensor('float32', input, [1, 3, SIZE, SIZE]) });
  if (signal.aborted) throw new Error('Scan cancelled.');
  const tensor = output[session.outputNames[0]];
  const values = tensor?.data;
  if (!values || tensor.dims.length !== 3 || tensor.dims[2] !== 6) throw new Error('The offline detector returned an unexpected result.');
  const detections: DetectionResult['detections'] = [];
  const found = new Map<string, DetectionResult['ingredients'][number]>();
  const xScale = original.width / resizedWidth;
  const yScale = original.height / resizedHeight;
  for (let row = 0; row < tensor.dims[1]; row++) {
    const index = row * 6;
    const confidence = Number(values[index + 4]);
    const label = labels[Math.round(Number(values[index + 5]))];
    if (!label || !Number.isFinite(confidence) || confidence < 0.1) continue;
    const name = ALIASES[label] ?? label.replace(/_/g, ' ');
    const x1 = clamp((Number(values[index]) - padX) * xScale, original.width);
    const y1 = clamp((Number(values[index + 1]) - padY) * yScale, original.height);
    const x2 = clamp((Number(values[index + 2]) - padX) * xScale, original.width);
    const y2 = clamp((Number(values[index + 3]) - padY) * yScale, original.height);
    if (x2 <= x1 || y2 <= y1) continue;
    detections.push({ name, label, confidence, bbox_xyxy: [x1, y1, x2, y2], source_model: 'offline-yolov8n' });
    const current = found.get(name);
    if (!current || (current.confidence ?? 0) < confidence) found.set(name, { name: name[0].toUpperCase() + name.slice(1), label, confidence });
  }
  return { ingredients: [...found.values()], detections, width: original.width, height: original.height };
}
