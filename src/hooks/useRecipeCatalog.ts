import { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { recipes as previewRecipes, Recipe } from '../data/recipes';
import { CookingStyle, destinations as previewDestinations } from '../data/cookingStyles';
import { loadCatalog } from '../services/catalog';

type Destination = { name: string; style: Exclude<CookingStyle, 'Any style'> };
export function useRecipeCatalog() {
  const { session, preview, recovery } = useAuth();
  const enabled = Boolean(session?.user.email_confirmed_at && !recovery && !preview);
  const [recipes, setRecipes] = useState<Recipe[]>(preview ? previewRecipes : []);
  const [destinations, setDestinations] = useState<readonly Destination[]>(preview ? previewDestinations : []);
  const [loaded, setLoaded] = useState(false);
  const [catalogError, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!enabled) return;
    let active = true;
    void loadCatalog().then(catalog => {
      if (!active) return;
      setRecipes(catalog.recipes); setDestinations(catalog.destinations);
    }).catch(() => { if (active) setError('Could not load recipes.'); })
      .finally(() => { if (active) setLoaded(true); });
    return () => { active = false; };
  }, [enabled, attempt]);
  return { recipes, destinations, catalogLoading: enabled && !loaded && !catalogError, catalogError,
    reloadCatalog: () => { setLoaded(false); setError(''); setAttempt(value => value + 1); } };
}
