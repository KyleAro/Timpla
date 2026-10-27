import { useRef, useState } from 'react';
import { authError } from './validation';

export function useAuthAction() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const running = useRef(false);
  async function run(action: () => Promise<void>) {
    if (running.current) return;
    running.current = true;
    setBusy(true);
    setError('');
    try { await action(); }
    catch (cause) { setError(authError(cause)); }
    finally { running.current = false; setBusy(false); }
  }
  return { busy, error, setError, run };
}
