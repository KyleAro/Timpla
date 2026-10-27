import { initialScanState, RecentScan, scanReducer, SelectedDish } from './scanHistory';
import { createContext, PropsWithChildren, useContext, useEffect, useReducer, useRef, useState } from 'react';
import { useSavedRecipes } from '../hooks/useSavedRecipes';
import { detectIngredients } from '../services/detection';
import { useAuth } from '../auth/AuthContext';
import { useAccountSettings } from '../hooks/useAccountSettings';
import { useRecipeCatalog } from '../hooks/useRecipeCatalog';

type CookingState = ReturnType<typeof useAccountSettings> & ReturnType<typeof useRecipeCatalog> & {
  detecting: boolean;
  detectionError: string;
  retryDetection: () => void;
  huntIngredients: Record<string, string[]>;
  toggleHuntIngredient: (recipeId: string, ingredient: string) => void;
  savedRecipeIds: string[];
  toggleSavedRecipe: (id: string) => void;
  recentScans: RecentScan[];
  selectDish: (dish: SelectedDish) => void;
  openRecentScan: (id: string) => void;
  ingredients: string[];
  setIngredients: (value: string[]) => void;
  photo: string | null;
  setPhoto: (value: string | null) => void;
};
const CookingContext = createContext<CookingState | null>(null);

export function CookingProvider({ children }: PropsWithChildren) {
  const { session, preview } = useAuth();
  const accountId = preview ? 'preview' : session?.user.id ?? 'signed-out';
  const account = useAccountSettings();
  const catalog = useRecipeCatalog();
  const [huntIngredients, setHuntIngredients] = useState<Record<string, string[]>>({});
  function toggleHuntIngredient(recipeId: string, ingredient: string) {
    setHuntIngredients((current) => {
      const items = current[recipeId] ?? [];
      return { ...current, [recipeId]: items.includes(ingredient) ? items.filter((name) => name !== ingredient) : [...items, ingredient] };
    });
  }
  const savedRecipes = useSavedRecipes(accountId);
  const [scanState, dispatchScan] = useReducer(scanReducer, initialScanState);
  const { ingredients, photo, recentScans } = scanState;
  const [detection, setDetection] = useState({ id: '', pending: false, error: '' });
  const request = useRef<AbortController | null>(null);
  useEffect(() => () => request.current?.abort(), []);
  async function runDetection(id: string, uri: string) {
    request.current?.abort();
    const controller = new AbortController();
    request.current = controller;
    setDetection({ id, pending: true, error: '' });
    const timeout = setTimeout(() => controller.abort(), 120_000);
    try {
      const detected = await detectIngredients(uri, controller.signal);
      if (controller.signal.aborted || request.current !== controller) return;
      dispatchScan({ type: 'detected', id, ingredients: detected });
      setDetection({ id, pending: false, error: '' });
    } catch (error) {
      if (request.current === controller) setDetection({ id, pending: false, error: controller.signal.aborted ? 'Scan timed out. Try again.' : error instanceof Error ? error.message : 'Could not scan this photo.' });
    } finally { clearTimeout(timeout); }
  }
  function retryDetection() {
    if (scanState.activeId && photo) void runDetection(scanState.activeId, photo);
  }
  function setIngredients(names: string[]) { dispatchScan({ type: 'ingredients', names }); }
  function setPhoto(value: string | null) {
    if (!value) { request.current?.abort(); request.current = null; setDetection({ id: '', pending: false, error: '' }); dispatchScan({ type: 'detach' }); return; }
    const createdAt = Date.now();
    const id = `${createdAt}-${Math.random().toString(36).slice(2)}`;
    dispatchScan({ type: 'capture', scan: { id, photo: value, createdAt, ingredients: [], selectedDish: null } });
    void runDetection(id, value);
  }
  function openRecentScan(id: string) { dispatchScan({ type: 'open', id }); }
  function selectDish(dish: SelectedDish) { dispatchScan({ type: 'select', dish }); }
  return (
    <CookingContext.Provider value={{ ...account, ...catalog, detecting: detection.id === scanState.activeId && detection.pending, detectionError: detection.id === scanState.activeId ? detection.error : '', retryDetection, huntIngredients, toggleHuntIngredient, ...savedRecipes, selectDish, recentScans, openRecentScan, ingredients, setIngredients, photo, setPhoto }}>
      {children}
    </CookingContext.Provider>
  );
}

export function useCooking() {
  const state = useContext(CookingContext);
  if (!state) throw new Error('useCooking must be used inside CookingProvider');
  return state;
}

