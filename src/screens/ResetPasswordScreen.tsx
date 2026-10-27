import { useState } from 'react';
import { router } from 'expo-router';
import { useAuth } from '../auth/AuthContext';
import { useAuthAction } from '../auth/useAuthAction';
import { passwordError } from '../auth/validation';
import { AuthButton, AuthForm, AuthInput, AuthLink } from '../components/AuthForm';

export default function ResetPasswordScreen() {
  const { session, recovery, updatePassword, signOut } = useAuth();
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const { busy, error, setError, run } = useAuthAction();
  if (!session || !recovery) return <AuthForm title="Reset your password" subtitle="Open your reset email or verify its code first."><AuthLink title="Request reset email" onPress={() => router.replace('/forgot-password')} /></AuthForm>;
  function submit() {
    const invalid = passwordError(password) || (password !== confirmation ? 'Passwords do not match.' : '');
    if (invalid) { setError(invalid); return; }
    void run(async () => {
      await updatePassword(password);
      setPassword(''); setConfirmation('');
      router.replace({ pathname: '/', params: { reset: 'done' } });
    });
  }
  return <AuthForm title="Set a new password" error={error}>
    <AuthInput password accessibilityLabel="New password" placeholder="New password · at least 8 characters" value={password} onChangeText={setPassword} autoComplete="new-password" textContentType="newPassword" autoCapitalize="none" autoCorrect={false} editable={!busy} />
    <AuthInput password accessibilityLabel="Confirm new password" placeholder="Confirm password" value={confirmation} onChangeText={setConfirmation} autoComplete="new-password" textContentType="newPassword" autoCapitalize="none" autoCorrect={false} editable={!busy} returnKeyType="go" onSubmitEditing={submit} />
    <AuthButton title="Save password" onPress={submit} busy={busy} />
    <AuthLink title="Cancel" disabled={busy} onPress={() => { void run(async () => { await signOut(); router.replace('/'); }); }} />
  </AuthForm>;
}
