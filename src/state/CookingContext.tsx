import { initialScanState, RecentScan, scanReducer, SelectedDish } from './scanHistory';
import { createContext, PropsWithChildren, useContext, useEffect, useReducer, useRef, useState } from 'react';
import { detectIngredients } from '../services/detection';
import { useSavedRecipes } from '../hooks/useSavedRecipes';
import { useAuth } from '../auth/AuthContext';
import { useAccountSettings } from '../hooks/useAccountSettings';
import type { Recipe } from '../types/recipe';
import { destinations } from '../data/cookingStyles';

const recipes: Recipe[] = [];

type CookingState = ReturnType<typeof useAccountSettings> & {
  recipes: Recipe[];
  destinations: typeof destinations;
  detecting: boolean;
  detectionError: string;
  detectionComplete: boolean;
  retryDetection: () => void;
  scanIngredients: RecentScan['ingredients'];
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
  const [detection, setDetection] = useState({ id: '', status: 'idle', error: '' });
  const request = useRef<AbortController | null>(null);
  function cancelDetection() { request.current?.abort(); request.current = null; }
  // The layout keys this provider by account; unmount cancels requests on account changes.
  useEffect(() => () => { request.current?.abort(); request.current = null; }, []);
  async function runDetection(id: string, uri: string) {
    cancelDetection();
    const controller = new AbortController();
    request.current = controller;
    setDetection({ id, status: 'pending', error: '' });
    const timeout = setTimeout(() => controller.abort(), 120_000);
    try {
      const detected = await detectIngredients(uri, controller.signal);
      if (controller.signal.aborted || request.current !== controller) return;
      dispatchScan({ type: 'detected', id, ingredients: detected });
      setDetection({ id, status: 'complete', error: '' });
    } catch (error) {
      if (request.current !== controller) return;
      setDetection({ id, status: 'error', error: controller.signal.aborted ? 'Detection timed out. Retry or add ingredients manually.' : error instanceof Error ? error.message : 'Could not detect ingredients. Retry or add them manually.' });
    } finally { clearTimeout(timeout); }
  }
  function retryDetection() {
    if (scanState.activeId && photo) void runDetection(scanState.activeId, photo);
  }
  function setIngredients(names: string[]) { dispatchScan({ type: 'ingredients', names }); }
  function setPhoto(value: string | null) {
    cancelDetection();
    setDetection({ id: '', status: 'idle', error: '' });
    if (!value) { dispatchScan({ type: 'detach' }); return; }
    const createdAt = Date.now();
    const id = `${createdAt}-${Math.random().toString(36).slice(2)}`;
    dispatchScan({ type: 'capture', scan: { id, photo: value, createdAt, ingredients: [], selectedDish: null } });
    void runDetection(id, value);
  }
  function openRecentScan(id: string) {
    cancelDetection();
    setDetection({ id: '', status: 'idle', error: '' });
    dispatchScan({ type: 'open', id });
  }
  const activeDetection = detection.id === scanState.activeId;
  const scanIngredients = recentScans.find(item => item.id === scanState.activeId)?.ingredients ?? [];
  function selectDish(dish: SelectedDish) { dispatchScan({ type: 'select', dish }); }
  return (
    <CookingContext.Provider value={{ ...account, recipes, destinations, detecting: activeDetection && detection.status === 'pending', detectionComplete: activeDetection && detection.status === 'complete', detectionError: activeDetection ? detection.error : '', retryDetection, scanIngredients, huntIngredients, toggleHuntIngredient, ...savedRecipes, selectDish, recentScans, openRecentScan, ingredients, setIngredients, photo, setPhoto }}>
      {children}
    </CookingContext.Provider>
  );
}

export function useCooking() {
  const state = useContext(CookingContext);
  if (!state) throw new Error('useCooking must be used inside CookingProvider');
  return state;
}

