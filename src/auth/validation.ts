export function cleanEmail(value: string) { return value.trim().toLowerCase(); }
export function emailError(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail(value)) ? '' : 'Enter a valid email address.';
}
export function passwordError(value: string) {
  return value.length >= 8 ? '' : 'Use at least 8 characters for your password.';
}
export function authError(error: unknown) {
  const code = typeof error === 'object' && error !== null && 'code' in error ? String(error.code) : '';
  const messages: Record<string, string> = {
    invalid_credentials: 'Incorrect email or password.',
    email_not_confirmed: 'Confirm your email before logging in.',
    user_already_exists: 'An account already exists. Log in or reset your password.',
    email_exists: 'An account already exists. Log in or reset your password.',
    weak_password: 'Choose a stronger password with at least 8 characters.',
    same_password: 'Choose a different password.',
    otp_expired: 'This code or link has expired. Request a new one.',
    over_email_send_rate_limit: 'Please wait before requesting another email.',
    over_request_rate_limit: 'Too many attempts. Please try again shortly.',
    signup_disabled: 'Registration is temporarily unavailable.',
  };
  if (messages[code]) return messages[code];
  if (error instanceof Error && /network|fetch|connection/i.test(error.message)) return 'Could not connect. Check your internet and try again.';
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.';
}

// Accept only supported Auth values; never treat arbitrary query data as a session.
export function readAuthCallback(url: string) {
  const parsed = new URL(url);
  const query = parsed.searchParams;
  const hash = new URLSearchParams(parsed.hash.replace(/^#/, ''));
  const get = (key: string) => hash.get(key) ?? query.get(key);
  return {
    error: get('error_description') ?? get('error'),
    code: get('code'),
    accessToken: get('access_token'),
    refreshToken: get('refresh_token'),
    recovery: get('type') === 'recovery',
  };
}
