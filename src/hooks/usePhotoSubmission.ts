import { useCallback, useEffect, useRef, useState } from 'react';
import { router, useFocusEffect } from 'expo-router';
import { useCooking } from '../state/CookingContext';

export function usePhotoSubmission() {
  const { setPhoto } = useCooking();
  const [processing, setProcessing] = useState(false);
  const [notice, setNotice] = useState<'empty' | 'error' | null>(null);
  const pending = useRef(false);
  const setPhotoRef = useRef(setPhoto);
  useEffect(() => { setPhotoRef.current = setPhoto; }, [setPhoto]);
  useFocusEffect(useCallback(() => () => {
    if (pending.current) { pending.current = false; void setPhotoRef.current(null); }
  }, []));
  async function submit(uri: string) {
    if (pending.current) return;
    pending.current = true;
    setProcessing(true);
    setNotice(null);
    try {
      const outcome = await setPhotoRef.current(uri);
      if (!pending.current) return;
      pending.current = false;
      if (outcome === 'found') router.push('/ingredients');
      else if (outcome === 'empty' || outcome === 'error') setNotice(outcome);
    } finally { setProcessing(false); }
  }
  function dismiss() { setNotice(null); void setPhotoRef.current(null); }
  return { submit, processing, notice, dismiss };
}
