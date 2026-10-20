import { File } from 'expo-file-system';
import { Image, Platform } from 'react-native';

export const MAX_PHOTO_BYTES = 5_000_000;

export class PhotoValidationError extends Error {}

export function validatePhotoSize(size: number) {
  if (!Number.isFinite(size) || size <= 0) throw new PhotoValidationError('Choose a valid image.');
  if (size > MAX_PHOTO_BYTES) throw new PhotoValidationError('Photo must be 5 MB or smaller.');
}

// Check the actual returned file, rather than trusting its name or picker metadata.
export async function validatePhoto(uri: string, mediaType?: string | null, mimeType?: string | null) {
  if ((mediaType && mediaType !== 'image') || (mimeType && !mimeType.toLowerCase().startsWith('image/'))) {
    throw new PhotoValidationError('Choose an image file.');
  }
  let size: number;
  if (Platform.OS === 'web') {
    const response = await fetch(uri);
    if (!response.ok) throw new PhotoValidationError('Choose a valid image.');
    const blob = await response.blob();
    if (blob.type && !blob.type.startsWith('image/')) throw new PhotoValidationError('Choose an image file.');
    size = blob.size;
  } else {
    const file = new File(uri);
    if (!file.exists) throw new PhotoValidationError('Choose a valid image.');
    size = file.size;
  }
  validatePhotoSize(size);
  try {
    const dimensions = await Image.getSize(uri);
    if (dimensions.width <= 0 || dimensions.height <= 0) throw new Error('Empty image');
  } catch {
    throw new PhotoValidationError('Choose a valid image.');
  }
}
