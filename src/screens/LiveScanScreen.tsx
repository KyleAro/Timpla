import { CameraView, useCameraPermissions } from 'expo-camera';
import { ImageManipulator, SaveFormat } from 'expo-image-manipulator';
import Svg, { Path } from 'react-native-svg';
import { CaptureFrame, captureMask, photoCrop } from '../utils/photoCrop';
import { PhotoValidationError, validatePhoto } from '../utils/validatePhoto';
import { router, useIsFocused } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useIngredientPhoto } from '../hooks/useIngredientPhoto';
import { AppIcon } from '../components/AppIcon';
import { useCooking } from '../state/CookingContext';
import { useTheme } from '../theme/ThemeContext';

export default function LiveScanScreen() {
  const { palette } = useTheme();

  const { setPhoto } = useCooking();
  const [permission, requestPermission] = useCameraPermissions();
  const isFocused = useIsFocused();
  const { pick, busy, error: uploadError } = useIngredientPhoto();
  const [error, setError] = useState('');
  const askedPermission = useRef(false);
  useEffect(() => {
    if (!isFocused || !permission || permission.granted || permission.status !== 'undetermined' || askedPermission.current) return;
    askedPermission.current = true;
    void requestPermission().catch(() => setError('Could not request camera access. Try again or upload a photo.'));
  }, [isFocused, permission, requestPermission]);
  const camera = useRef<CameraView>(null);
  const preview = useRef<View>(null);
  const guide = useRef<View>(null);
  const [captureFrame, setCaptureFrame] = useState<CaptureFrame | null>(null);
  const measureGuide = useCallback(() => {
    preview.current?.measureInWindow((px, py, width, height) => {
      guide.current?.measureInWindow((gx, gy, gw, gh) => {
        if (width > 0 && height > 0 && gw > 0 && gh > 0) setCaptureFrame({ viewport: { width, height }, rect: { x: gx - px, y: gy - py, width: gw, height: gh } });
      });
    });
  }, []);
  const [ready, setReady] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [torchOn, setTorchOn] = useState(false);
  const [pendingPhoto, setPendingPhoto] = useState<string | null>(null);
  const captureLock = useRef(false);
  const confirmLock = useRef(false);

  const assignCamera = useCallback((instance: CameraView | null) => {
    camera.current = instance;
    if (!instance) { setReady(false); setTorchOn(false); }
  }, []);

  async function capture() {
    if (!ready || !captureFrame || capturing || captureLock.current || !camera.current) return;
    const frame = captureFrame;
    captureLock.current = true;
    confirmLock.current = false;
    setCapturing(true);
    setError('');
    try {
      const picture = await camera.current.takePictureAsync({ quality: 0.9, skipProcessing: false });
      if (!picture?.uri) throw new Error('No photo was returned');
      const crop = photoCrop(frame, { width: picture.width, height: picture.height });
      const context = ImageManipulator.manipulate(picture.uri);
      try {
        context.crop(crop);
        const rendered = await context.renderAsync();
        try {
          const cropped = await rendered.saveAsync({ format: SaveFormat.JPEG, compress: 0.9 });
          await validatePhoto(cropped.uri, 'image', 'image/jpeg');
          setReady(false);
          setPendingPhoto(cropped.uri);
        } finally { rendered.release(); }
      } finally { context.release(); }
    } catch (error) {
      setError(error instanceof PhotoValidationError ? error.message : 'Could not capture a photo. Please try again.');
    } finally {
      captureLock.current = false;
      setCapturing(false);
    }
  }

  if (pendingPhoto) return (
    <View style={styles.screen}>
      <Image source={{ uri: pendingPhoto }} accessibilityLabel="Captured ingredient photo" style={StyleSheet.absoluteFill} resizeMode="contain" />
      <SafeAreaView pointerEvents="box-none" style={styles.reviewOverlay}>
        <View style={styles.reviewActions}>
          <Pressable accessibilityRole="button" accessibilityLabel="Retake photo" onPress={() => { setPendingPhoto(null); setError(''); confirmLock.current = false; }} style={styles.reviewButton}><AppIcon name="close" size={30} color="#FFFFFF" /></Pressable>
          <Pressable accessibilityRole="button" accessibilityLabel="Use this photo" onPress={() => {
            if (confirmLock.current) return;
            confirmLock.current = true;
            setPhoto(pendingPhoto);
            setPendingPhoto(null);
            router.push('/ingredients');
          }} style={[styles.reviewButton, { backgroundColor: palette.accent }]}><AppIcon name="check" size={30} color="#FFFFFF" /></Pressable>
        </View>
      </SafeAreaView>
    </View>
  );

  return (
    <View ref={preview} collapsable={false} onLayout={measureGuide} style={styles.screen}>
      {permission?.granted && isFocused && !busy ? <CameraView ref={assignCamera} style={StyleSheet.absoluteFill} facing="back" enableTorch={torchOn} onCameraReady={() => { setReady(true); setError(''); }} onMountError={() => { setReady(false); setError('Could not open the camera. Try uploading a photo.'); }} /> : null}
      {permission?.granted && isFocused && !busy && captureFrame ? <Svg pointerEvents="none" accessible={false} width="100%" height="100%" style={StyleSheet.absoluteFill}><Path d={captureMask(captureFrame)} fill="#000000" fillOpacity={0.65} fillRule="evenodd" /></Svg> : null}
      <SafeAreaView pointerEvents="box-none" style={styles.overlay}>
        <View pointerEvents="box-none" style={styles.topControls}>
          <Pressable accessibilityRole="button" accessibilityLabel="Close camera" disabled={capturing} onPress={() => router.replace('/home')} style={styles.close}><AppIcon name="back" size={26} color="#FFFFFF" /></Pressable>
          <Pressable accessibilityRole="switch" accessibilityLabel="Flashlight" accessibilityState={{ checked: torchOn, disabled: !ready || busy || capturing }} disabled={!ready || busy || capturing} onPress={() => setTorchOn((value) => !value)} style={[styles.close, torchOn && { backgroundColor: palette.accent }, (!ready || busy || capturing) && styles.disabled]}><AppIcon name={torchOn ? 'flash' : 'flash-off'} size={25} color="#FFFFFF" /></Pressable>
        </View>
        <View pointerEvents="box-none" style={styles.middle}>
          {permission?.granted && isFocused && !busy ? <View ref={guide} collapsable={false} onLayout={measureGuide} pointerEvents="none" accessible={false} style={styles.scanGuide} /> : null}
          {!permission ? <View style={styles.message}><ActivityIndicator color="#FFFFFF" /><Text style={styles.body}>Preparing camera…</Text></View> : !permission.granted ? <View style={styles.message}>
            <AppIcon name="camera" size={48} color="#FFFFFF" />
            <Text style={styles.title}>Camera access needed</Text>
            <Text style={styles.body}>{permission.canAskAgain ? 'Allow camera access to capture ingredients.' : 'Enable camera access in your phone settings, or upload a photo.'}</Text>
            {permission.canAskAgain && <Pressable accessibilityRole="button" onPress={() => { void requestPermission().catch(() => setError('Could not request camera access. Try Upload photo.')); }} style={[styles.permissionButton, { backgroundColor: palette.accent }]}><Text style={styles.buttonText}>Allow camera</Text></Pressable>}
          </View> : null}
        </View>
        <View style={styles.bottomControls}>
          {error || uploadError ? <Text accessibilityLiveRegion="polite" style={styles.error}>{error || uploadError}</Text> : null}
          <View style={styles.actions}>
            <Pressable accessibilityRole="button" accessibilityLabel="Upload ingredient photo" disabled={busy || capturing} onPress={() => void pick('library')} style={[styles.upload, (busy || capturing) && styles.disabled]}>
              {busy ? <ActivityIndicator color="#FFFFFF" /> : <AppIcon name="upload" size={27} color="#FFFFFF" />}<Text style={styles.uploadText}>Upload</Text>
            </Pressable>
            <Pressable accessibilityRole="button" accessibilityLabel="Capture ingredients photo" disabled={!ready || !captureFrame || capturing || busy || !permission?.granted} onPress={() => void capture()} style={[styles.shutter, (!ready || !captureFrame || capturing || busy || !permission?.granted) && styles.disabled]}>
              {capturing ? <ActivityIndicator color="#FFFFFF" /> : <View style={styles.shutterInner} />}
            </Pressable>
            <View style={styles.spacer} />
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000000' },
  reviewOverlay: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0, justifyContent: 'flex-end' },
  reviewActions: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', backgroundColor: '#00000080', paddingVertical: 24 },
  reviewButton: { width: 64, height: 64, borderRadius: 32, backgroundColor: '#333333', alignItems: 'center', justifyContent: 'center' },
  overlay: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0, justifyContent: 'space-between' },
  topControls: { paddingHorizontal: 10, paddingTop: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  close: { width: 48, height: 48, borderRadius: 24, backgroundColor: '#00000080', alignItems: 'center', justifyContent: 'center' },
  middle: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 30 },
  scanGuide: { position: 'absolute', top: '3%', bottom: '12%', left: '8%', right: '8%', borderWidth: 1.5, borderColor: '#FFFFFF', borderRadius: 20 },
  message: { alignItems: 'center', gap: 16, maxWidth: 340 },
  title: { color: '#FFFFFF', fontSize: 22, fontWeight: '700', textAlign: 'center' },
  body: { color: '#FFFFFF', fontSize: 15, lineHeight: 23, textAlign: 'center' },
  permissionButton: { minHeight: 50, paddingHorizontal: 24, borderRadius: 25, justifyContent: 'center' },
  buttonText: { color: '#FFFFFF', fontWeight: '700', fontSize: 16 },
  bottomControls: { backgroundColor: 'transparent', paddingTop: 18, paddingBottom: 22, paddingHorizontal: 24 },
  actions: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', maxWidth: 440, width: '100%', alignSelf: 'center' },
  upload: { width: 76, minHeight: 64, alignItems: 'center', justifyContent: 'center', gap: 6 },
  uploadText: { color: '#FFFFFF', fontSize: 12, fontWeight: '600' },
  shutter: { width: 78, height: 78, borderRadius: 39, borderWidth: 4, borderColor: '#FFFFFF', alignItems: 'center', justifyContent: 'center' },
  shutterInner: { width: 62, height: 62, borderRadius: 31, backgroundColor: '#FFFFFF' },
  spacer: { width: 76 },
  disabled: { opacity: 0.45 },
  error: { color: '#FFFFFF', backgroundColor: '#00000099', fontSize: 14, lineHeight: 21, padding: 12, borderRadius: 10, textAlign: 'center', marginBottom: 14 },
});



