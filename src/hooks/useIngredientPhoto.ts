import { useRef, useState } from 'react';
import { Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { router } from 'expo-router';
import { useCooking } from '../state/CookingContext';
import { PhotoValidationError, validatePhoto, validatePhotoSize } from '../utils/validatePhoto';

export function useIngredientPhoto() {
  const { setPhoto } = useCooking();
  const lock = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function pick(source: 'camera' | 'library') {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError('');
    try {
      if (source === 'camera' && Platform.OS !== 'web') {
        const permission = await ImagePicker.requestCameraPermissionsAsync();
        if (!permission.granted) {
          setError(permission.canAskAgain ? 'Allow camera access to take an ingredient photo, or use Upload.' : 'Camera access is off. Enable it in your phone settings, or use Upload.');
          return;
        }
      }
      const options: ImagePicker.ImagePickerOptions = { mediaTypes: ['images'], allowsEditing: false, quality: 0.8 };
      const result = source === 'camera' ? await ImagePicker.launchCameraAsync(options) : await ImagePicker.launchImageLibraryAsync(options);
      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        if (asset.fileSize != null) validatePhotoSize(asset.fileSize);
        await validatePhoto(asset.uri, asset.type, asset.mimeType);
        setPhoto(asset.uri);
        router.push('/ingredients');
      }
    } catch (error) {
      setError(error instanceof PhotoValidationError ? error.message : 'Could not open the photo picker. Try again or add ingredients manually.');
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return { pick, busy, error };
}
