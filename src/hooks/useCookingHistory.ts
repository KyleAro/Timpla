import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useRef, useState } from 'react';

export type CookedRecipe = { id: string; recipeId: string; name: string; cookedAt: number };
export function useCookingHistory(accountId: string) {
  const key = `timpla.${accountId}.cooking-history`;
  const [cookingHistory, setHistory] = useState<CookedRecipe[]>([]);
  const [historyError, setError] = useState('');
  const current = useRef<CookedRecipe[]>([]);
  const ready = useRef(false);
  const writes = useRef(Promise.resolve());
  useEffect(() => {
    let active = true;
    void AsyncStorage.getItem(key).then(raw => {
      if (!active) return;
      let parsed: unknown = [];
      try { parsed = raw ? JSON.parse(raw) : []; } catch { /* Ignore malformed local data. */ }
      current.current = Array.isArray(parsed) ? parsed.filter((row): row is CookedRecipe => row && typeof row.id === 'string' && typeof row.recipeId === 'string' && typeof row.name === 'string' && Number.isFinite(row.cookedAt)) : [];
      setHistory(current.current);
      ready.current = true;
    }).catch(() => { if (active) setError('Could not load cooking history. Reopen the app to try again.'); });
    return () => { active = false; };
  }, [key]);
  async function recordCookedRecipe(recipeId: string, name: string) {
    if (!ready.current) throw new Error('Cooking history is still loading. Please try again.');
    const cookedAt = Date.now();
    const row = { id: `${cookedAt}-${Math.random().toString(36).slice(2)}`, recipeId, name, cookedAt };
    const operation = writes.current.catch(() => {}).then(async () => {
      const rows = [row, ...current.current];
      await AsyncStorage.setItem(key, JSON.stringify(rows));
      current.current = rows;
      setHistory(rows);
      setError('');
    });
    writes.current = operation;
    await operation;
  }
  return { cookingHistory, recordCookedRecipe, historyError };
}
