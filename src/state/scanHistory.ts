import { normalizeIngredient } from '../utils/normalizeIngredient';

export type ScanIngredient = { name: string; confidence: number | null; label?: string };
export type ScanDetection = {
  name: string;
  label: string;
  confidence: number;
  bbox_xyxy: [number, number, number, number];
  source_model?: string;
};
export type SelectedDish = { id: string; name: string; required: string[] };
export type RecentScan = {
  saved?: boolean;
  id: string;
  photo: string;
  createdAt: number;
  ingredients: ScanIngredient[];
  detections?: ScanDetection[];
  imageWidth?: number;
  imageHeight?: number;
  selectedDish: SelectedDish | null;
  dismissedIngredients?: string[];
};
export type ScanState = { photo: string | null; ingredients: string[]; activeId: string | null; recentScans: RecentScan[] };
export type ScanAction =
  | { type: 'delete'; id: string }
  | { type: 'save' }
  | { type: 'discard' }
  | { type: 'restore'; scans: RecentScan[] }
  | { type: 'capture'; scan: RecentScan }
  | { type: 'detected'; id: string; ingredients: ScanIngredient[]; detections: ScanDetection[]; imageWidth?: number; imageHeight?: number }
  | { type: 'reset' }
  | { type: 'detach' }
  | { type: 'ingredients'; names: string[] }
  | { type: 'select'; dish: SelectedDish }
  | { type: 'open'; id: string };
export const initialScanState: ScanState = { photo: null, ingredients: [], activeId: null, recentScans: [] };
export function scanReducer(state: ScanState, action: ScanAction): ScanState {
  switch (action.type) {
    case 'delete': return { ...state, recentScans: state.recentScans.filter(scan => scan.id !== action.id), ...(state.activeId === action.id ? { activeId: null, photo: null, ingredients: [] } : {}) };
    case 'save': return { ...state, recentScans: state.recentScans.map(scan => scan.id === state.activeId ? { ...scan, saved: true } : scan) };
    case 'discard': return { ...state, photo: null, ingredients: [], activeId: null, recentScans: state.recentScans.filter(scan => scan.id !== state.activeId) };
    case 'restore': return { ...state, recentScans: [...state.recentScans, ...action.scans.filter(scan => !state.recentScans.some(current => current.id === scan.id))].slice(0, 20) };
    case 'reset': return initialScanState;
    case 'detected': {
      if (state.activeId !== action.id) return state;
      const scan = state.recentScans.find(item => item.id === action.id);
      if (!scan) return state;
      const dismissed = new Set(scan.dismissedIngredients ?? []);
      const merged = new Map(scan.ingredients.map(item => [normalizeIngredient(item.name), item]));
      for (const item of action.ingredients) {
        const key = normalizeIngredient(item.name);
        if (!dismissed.has(key) && !merged.has(key)) merged.set(key, item);
      }
      const ingredients = [...merged.values()];
      return {
        ...state,
        ingredients: ingredients.map(item => item.name),
        recentScans: state.recentScans.map(item => item.id === action.id ? {
          ...item,
          ingredients,
          detections: action.detections,
          imageWidth: action.imageWidth,
          imageHeight: action.imageHeight,
        } : item),
      };
    }
    case 'capture': return { photo: action.scan.photo, ingredients: [], activeId: action.scan.id, recentScans: [action.scan, ...state.recentScans].slice(0, 20) };
    case 'detach': return { ...state, photo: null, activeId: null };
    case 'open': {
      const scan = state.recentScans.find(item => item.id === action.id);
      return scan ? { ...state, activeId: scan.id, photo: scan.photo, ingredients: scan.ingredients.map(item => item.name) } : state;
    }
    case 'ingredients': return { ...state, ingredients: [...action.names], recentScans: state.recentScans.map(scan => {
      if (scan.id !== state.activeId) return scan;
      const selected = new Set(action.names.map(normalizeIngredient));
      const dismissed = new Set(scan.dismissedIngredients ?? []);
      for (const item of scan.ingredients) if (!selected.has(normalizeIngredient(item.name))) dismissed.add(normalizeIngredient(item.name));
      for (const name of selected) dismissed.delete(name);
      return { ...scan, dismissedIngredients: [...dismissed], ingredients: action.names.map(name => scan.ingredients.find(item => normalizeIngredient(item.name) === normalizeIngredient(name)) ?? { name, confidence: null }) };
    }) };
    case 'select': return { ...state, recentScans: state.recentScans.map(scan => scan.id === state.activeId ? { ...scan, selectedDish: { ...action.dish, required: [...action.dish.required] } } : scan) };
  }
}
