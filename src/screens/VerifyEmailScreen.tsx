import { useEffect, useState } from 'react';
import { Redirect, router, useLocalSearchParams } from 'expo-router';
import { useAuth } from '../auth/AuthContext';
import { useAuthAction } from '../auth/useAuthAction';
import { emailError } from '../auth/validation';
import { AuthButton, AuthForm, AuthInput, AuthLink } from '../components/AuthForm';

export default function VerifyEmailScreen() {
  const params = useLocalSearchParams<{ email?: string; mode?: string; resend?: string }>();
  const email = typeof params.email === 'string' ? params.email : '';
  const kind = params.mode === 'recovery' ? 'recovery' : 'signup';
  const { session, recovery, verifyCode, resendConfirmation, sendReset } = useAuth();
  const [token, setToken] = useState('');
  const [seconds, setSeconds] = useState(params.resend === 'true' ? 0 : 60);
  const [notice, setNotice] = useState('');
  const { busy, error, setError, run } = useAuthAction();
  useEffect(() => {
    const timer = setInterval(() => setSeconds(current => Math.max(0, current - 1)), 1000);
    return () => clearInterval(timer);
  }, []);
  if (emailError(email)) return <Redirect href="/" />;
  if (session && recovery) return <Redirect href="/reset-password" />;
  if (session && kind === 'signup') return <Redirect href="/home" />;
  function submit() {
    if (!/^\d{8}$/.test(token)) { setError('Enter the 8-digit code from your email.'); return; }
    void run(async () => { await verifyCode(email, token, kind); setToken(''); });
  }
  function resend() {
    if (seconds) return;
    void run(async () => {
      if (kind === 'recovery') await sendReset(email);
      else await resendConfirmation(email);
      setSeconds(60); setNotice('Email requested. Check your inbox and Spam.');
    });
  }
  return <AuthForm title={kind === 'recovery' ? 'Check your email' : 'Confirm your email'} subtitle={kind === 'recovery' ? `If an account exists for ${email}, you’ll receive a reset email. Enter its code here.` : `Enter the code sent to ${email}.`} error={error} notice={notice}>
    <AuthInput accessibilityLabel="Email verification code" placeholder="8-digit code" value={token} onChangeText={value => setToken(value.replace(/\D/g, '').slice(0, 8))} keyboardType="number-pad" autoComplete="one-time-code" textContentType="oneTimeCode" maxLength={8} editable={!busy} returnKeyType="go" onSubmitEditing={submit} />
    <AuthButton title="Verify code" onPress={submit} busy={busy} />
    <AuthLink title={seconds ? `Resend email in ${seconds}s` : 'Resend email'} onPress={resend} disabled={busy || seconds > 0} />
    <AuthLink title="Back to log in" onPress={() => router.replace('/')} disabled={busy} />
  </AuthForm>;
}
