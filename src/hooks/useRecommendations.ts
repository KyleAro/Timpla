import { useEffect, useState } from 'react';
import { useCooking } from '../state/CookingContext';
import { getRecommendations, type Recommendation } from '../services/recommendations';

export function useRecommendations() {
  const { ingredients, exclusions, allergies, diet, detecting } = useCooking();
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{ key: string; items: Recommendation[]; error: string } | null>(null);
  const requestKey = JSON.stringify({ responseVersion: 2, available: ingredients, excluded: exclusions, allergies, diet });
  const canRequest = ingredients.length > 0 && !detecting;
  const current = result?.key === requestKey ? result : null;
  useEffect(() => {
    if (!canRequest) return;
    const controller = new AbortController();
    let timedOut = false;
    const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, 30_000);
    const input = JSON.parse(requestKey) as { available: string[]; excluded: string[]; allergies: string[]; diet: string };
    void getRecommendations(input.available, input.excluded, controller.signal, { allergies: input.allergies, diet: input.diet })
      .then(items => { if (!controller.signal.aborted) setResult({ key: requestKey, items, error: '' }); })
      .catch((error: unknown) => {
        if (!controller.signal.aborted || timedOut) setResult({ key: requestKey, items: [], error: error instanceof Error && error.message.includes('saved restrictions') ? error.message : timedOut ? 'This is taking longer than expected. Please try again.' : 'We couldn’t load your recipe matches. Check your connection and try again.' });
      }).finally(() => clearTimeout(timeout));
    return () => { clearTimeout(timeout); controller.abort(); };
  }, [requestKey, canRequest, attempt]);
  return { current, loading: canRequest && !current, retry: () => { setResult(null); setAttempt(value => value + 1); } };
}
