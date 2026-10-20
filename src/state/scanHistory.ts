import { ingredientMatch, normalizeIngredient } from '../utils/ingredientMatch';

export type ScanIngredient = { name: string; confidence: number | null };
export type SelectedDish = { id: string; name: string; required: string[] };
export type RecentScan = { id: string; photo: string; createdAt: number; ingredients: ScanIngredient[]; selectedDish: SelectedDish | null };
export type ScanState = { photo: string | null; ingredients: string[]; activeId: string | null; recentScans: RecentScan[] };
export type ScanAction =
  | { type: 'capture'; scan: RecentScan }
  | { type: 'detected'; id: string; ingredients: ScanIngredient[] }
  | { type: 'detach' }
  | { type: 'ingredients'; names: string[] }
  | { type: 'select'; dish: SelectedDish }
  | { type: 'open'; id: string };
export const initialScanState: ScanState = { photo: null, ingredients: [], activeId: null, recentScans: [] };
export function scanReducer(state: ScanState, action: ScanAction): ScanState {
  switch (action.type) {
    case 'detected': {
      let activeIngredients = state.ingredients;
      const recentScans = state.recentScans.map((scan) => {
        if (scan.id !== action.id) return scan;
        const detected = new Map(action.ingredients.map((item) => [normalizeIngredient(item.name), item]));
        for (const item of scan.ingredients) if (!detected.has(normalizeIngredient(item.name))) detected.set(normalizeIngredient(item.name), item);
        const ingredients = [...detected.values()];
        if (state.activeId === scan.id) activeIngredients = ingredients.map((item) => item.name);
        return { ...scan, ingredients };
      });
      return { ...state, ingredients: activeIngredients, recentScans };
    }
    case 'capture': return { photo: action.scan.photo, ingredients: [], activeId: action.scan.id, recentScans: [action.scan, ...state.recentScans].slice(0, 20) };
    case 'detach': return { ...state, photo: null, activeId: null };
    case 'open': {
      const scan = state.recentScans.find((item) => item.id === action.id);
      return scan ? { ...state, activeId: scan.id, photo: scan.photo, ingredients: scan.ingredients.map((item) => item.name) } : state;
    }
    case 'ingredients': return { ...state, ingredients: [...action.names], recentScans: state.recentScans.map((scan) => scan.id === state.activeId ? { ...scan, ingredients: action.names.map((name) => scan.ingredients.find((item) => item.name === name) ?? { name, confidence: null }) } : scan) };
    case 'select': return { ...state, recentScans: state.recentScans.map((scan) => scan.id === state.activeId ? { ...scan, selectedDish: { ...action.dish, required: [...action.dish.required] } } : scan) };
  }
}
export function savedRecipeMatch(scan: RecentScan) {
  return scan.selectedDish ? ingredientMatch(scan.selectedDish.required, scan.ingredients.map((item) => item.name)) : null;
}
