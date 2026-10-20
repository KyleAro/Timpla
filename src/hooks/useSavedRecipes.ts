import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useRef, useState } from 'react';

const key = 'timpla.saved-recipes';
export function useSavedRecipes() {
  const [savedRecipeIds, setIds] = useState<string[]>([]);
  const current = useRef<string[]>([]);
  const hydrated = useRef(false);
  const edits = useRef(new Map<string, boolean>());
  const writes = useRef(Promise.resolve());
  function persist(ids: string[]) {
    writes.current = writes.current.then(() => AsyncStorage.setItem(key, JSON.stringify(ids))).catch(() => {});
  }
  useEffect(() => {
    let mounted = true;
    void AsyncStorage.getItem(key).then((raw) => {
      if (!mounted) return;
      let stored: unknown;
      try { stored = raw ? JSON.parse(raw) : []; } catch { stored = []; }
      const merged = new Set<string>(Array.isArray(stored) ? stored.filter((id): id is string => typeof id === 'string') : []);
      edits.current.forEach((saved, id) => { if (saved) merged.add(id); else merged.delete(id); });
      current.current = [...merged];
      setIds(current.current);
      hydrated.current = true;
      if (edits.current.size) persist(current.current);
      edits.current.clear();
    }).catch(() => {
      if (!mounted) return;
      hydrated.current = true;
      if (edits.current.size) persist(current.current);
      edits.current.clear();
    });
    return () => { mounted = false; };
  }, []);
  function toggleSavedRecipe(id: string) {
    const saved = !current.current.includes(id);
    current.current = saved ? [...current.current, id] : current.current.filter((item) => item !== id);
    setIds(current.current);
    if (hydrated.current) persist(current.current);
    else edits.current.set(id, saved);
  }
  return { savedRecipeIds, toggleSavedRecipe };
}
