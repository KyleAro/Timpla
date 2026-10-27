const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const ts = require('typescript');

function load(relativePath, dependencies = {}, development = true) {
  const filename = path.resolve(__dirname, '..', relativePath);
  const output = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(output, {
    module, exports: module.exports, URL, URLSearchParams, Map, Promise, Error, __DEV__: development,
    process: { env: {} },
    require(name) { if (name in dependencies) return dependencies[name]; throw new Error(`Unexpected dependency ${name}`); },
  }, { filename });
  return module.exports;
}
const validation = load('src/auth/validation.ts');
const userSession = { user: { id: 'account-a', email: 'cook@example.com', email_confirmed_at: '2026-01-01', user_metadata: { full_name: 'Test cook' } }, access_token: 'test-only', refresh_token: 'test-only' };
const settle = () => new Promise(resolve => setImmediate(resolve));

function harness({ development = true, stored = new Map(), initial = null, getSession } = {}) {
  let cursor = 0;
  let mounted = false;
  const hooks = [];
  const effects = [];
  const calls = [];
  let listener = () => {};
  const auth = {
    onAuthStateChange(callback) { listener = callback; return { data: { subscription: { unsubscribe() {} } } }; },
    getSession: getSession || (async () => ({ data: { session: initial }, error: null })),
    startAutoRefresh() {}, stopAutoRefresh() {},
    async signInWithPassword(input) { calls.push(['signIn', input]); listener('SIGNED_IN', userSession); return { data: { session: userSession }, error: null }; },
    async signUp(input) { calls.push(['signUp', input]); return { data: { session: null, user: { identities: [{}] } }, error: null }; },
    async verifyOtp(input) { calls.push(['verify', input]); listener('SIGNED_IN', userSession); return { data: { session: userSession }, error: null }; },
    async resetPasswordForEmail(...input) { calls.push(['reset', ...input]); return { error: null }; },
    async resend(input) { calls.push(['resend', input]); return { error: null }; },
    async updateUser(input) { calls.push(['update', input]); return { error: null }; },
    async signOut(input) { calls.push(['signOut', input]); listener('SIGNED_OUT', null); return { error: null }; },
    async setSession(input) { calls.push(['setSession', input]); listener('SIGNED_IN', userSession); return { data: { session: userSession }, error: null }; },
  };
  const react = {
    createContext: () => ({ Provider: 'provider' }),
    useState(initialValue) {
      const index = cursor++;
      if (!mounted) hooks[index] = typeof initialValue === 'function' ? initialValue() : initialValue;
      return [hooks[index], value => { hooks[index] = typeof value === 'function' ? value(hooks[index]) : value; }];
    },
    useRef(value) { const index = cursor++; if (!mounted) hooks[index] = { current: value }; return hooks[index]; },
    useEffect(callback) { cursor++; if (!mounted) effects.push(callback); },
  };
  const storage = { async getItem(key) { return stored.get(key) ?? null; }, async setItem(key, value) { stored.set(key, value); }, async removeItem(key) { stored.delete(key); } };
  const { AuthProvider } = load('src/auth/AuthContext.tsx', {
    react,
    'react/jsx-runtime': { jsx: (type, props) => ({ type, props }) },
    'react-native': { Platform: { OS: 'ios' }, AppState: { currentState: 'active', addEventListener: () => ({ remove() {} }) } },
    'expo-linking': { createURL: () => 'exp://test-device/--/auth/callback' },
    '@react-native-async-storage/async-storage': storage,
    './supabase': { supabase: { auth }, authClient: () => ({ auth }) },
    './validation': validation,
  }, development);
  const render = () => { cursor = 0; const result = AuthProvider({ children: null }); const first = !mounted; mounted = true; if (first) effects.forEach(effect => effect()); return result.props.value; };
  render();
  return { render, calls, auth, stored };
}

test('signup sends the name and normalized email without inventing a session', async () => {
  const h = harness(); await settle();
  assert.equal(await h.render().signUp('  Maria Santos  ', '  Cook@Example.COM ', 'a-good-password'), false);
  assert.equal(h.calls[0][1].email, 'cook@example.com');
  assert.equal(h.calls[0][1].options.data.full_name, 'Maria Santos');
  assert.equal(h.render().session, null);
});
test('development skip opens preview without signing in; production cannot enable it', async () => {
  const h = harness(); await settle(); h.render().enterPreview();
  assert.equal(h.render().preview, true); assert.equal(h.render().session, null); assert.equal(h.calls.length, 0);
  await h.render().signOut(); assert.equal(h.render().preview, false); assert.equal(h.calls.length, 0);
  const production = harness({ development: false }); await settle(); production.render().enterPreview();
  assert.equal(production.render().preview, false);
});
test('recovery is restricted before SIGNED_IN and remains restricted after restart', async () => {
  const h = harness(); await settle();
  await h.render().verifyCode('cook@example.com', '123456', 'recovery');
  assert.equal(h.render().recovery, true); assert.equal(h.render().session.user.id, 'account-a');
  const reload = harness({ initial: userSession, stored: h.stored }); await settle();
  assert.equal(reload.render().recovery, true);
  await reload.render().updatePassword('new-test-password');
  assert.equal(reload.render().session, null); assert.equal(reload.render().recovery, false);
  assert.equal(reload.calls.find(call => call[0] === 'signOut')[1].scope, 'local');
});
test('password update is rejected before recovery verification', async () => {
  const h = harness({ initial: userSession }); await settle();
  await assert.rejects(h.render().updatePassword('new-password'), /Verify the reset code/);
  assert.equal(h.calls.length, 0);
});
test('a stale startup lookup cannot overwrite a new signed-in session', async () => {
  let resolveInitial;
  const initial = new Promise(resolve => { resolveInitial = resolve; });
  const h = harness({ getSession: () => initial });
  await h.render().signIn('cook@example.com', 'test-password');
  resolveInitial({ data: { session: null }, error: null }); await settle();
  assert.equal(h.render().session.user.id, 'account-a'); assert.equal(h.render().loading, false);
});
test('failed recovery code restores the previous recovery state', async () => {
  const h = harness({ initial: userSession }); await settle();
  h.auth.verifyOtp = async () => ({ data: {}, error: new Error('Expired code') });
  await assert.rejects(h.render().verifyCode('cook@example.com', '111111', 'recovery'), /Expired code/);
  assert.equal(h.render().recovery, false);
});
test('an existing session does not open the reset form while its code is still being checked', async () => {
  const h = harness({ initial: userSession }); await settle();
  let finish;
  h.auth.verifyOtp = () => new Promise(resolve => { finish = resolve; });
  const verifying = h.render().verifyCode('cook@example.com', '123456', 'recovery');
  await settle();
  assert.equal(h.render().recovery, false);
  finish({ data: { session: userSession }, error: null });
  await verifying;
  assert.equal(h.render().recovery, true);
});
test('callback parses both token fragments and PKCE codes, preserving server errors', () => {
  const fragment = validation.readAuthCallback('timpla://auth/callback#access_token=test&refresh_token=refresh&type=recovery');
  assert.equal(fragment.recovery, true); assert.equal(fragment.accessToken, 'test');
  assert.equal(validation.readAuthCallback('https://example.com/auth/callback?code=code-value').code, 'code-value');
  assert.equal(validation.readAuthCallback('timpla://auth/callback#error_description=Expired%20link').error, 'Expired link');
});
test('callback exchanges a token once and rejects missing tokens', async () => {
  const h = harness(); await settle();
  const url = 'timpla://auth/callback#access_token=test&refresh_token=refresh&type=recovery';
  assert.equal(await h.render().handleCallback(url), 'reset');
  assert.equal(await h.render().handleCallback(url), 'reset');
  assert.equal(h.calls.filter(call => call[0] === 'setSession').length, 1);
  await assert.rejects(h.render().handleCallback('timpla://auth/callback'), /incomplete/);
});
test('validation and error mapping give useful feedback without accepting blank inputs', () => {
  assert.notEqual(validation.emailError('bad-address'), '');
  assert.equal(validation.emailError('test@example.com'), '');
  assert.notEqual(validation.passwordError('short'), '');
  assert.equal(validation.passwordError('eight123'), '');
  assert.equal(validation.authError({ code: 'invalid_credentials' }), 'Incorrect email or password.');
  assert.match(validation.authError({ code: 'otp_expired' }), /expired/);
});

test('normal session restoration, sign-in and sign-out keep account state consistent', async () => {
  const h = harness({ initial: userSession }); await settle();
  assert.equal(h.render().session.user.id, 'account-a'); assert.equal(h.render().recovery, false);
  await h.render().signOut(); assert.equal(h.render().session, null);
  await h.render().signIn('  Cook@Example.com ', 'test-password');
  assert.equal(h.calls.find(call => call[0] === 'signIn')[1].email, 'cook@example.com');
  assert.equal(h.render().session.user.id, 'account-a');
});

test('confirmation and reset requests normalize email and include app callback', async () => {
  const h = harness(); await settle();
  await h.render().resendConfirmation('  Cook@Example.com ');
  await h.render().sendReset('  Cook@Example.com ');
  const confirmation = h.calls.find(call => call[0] === 'resend')[1];
  assert.equal(confirmation.type, 'signup'); assert.equal(confirmation.email, 'cook@example.com');
  assert.equal(confirmation.options.emailRedirectTo, 'exp://test-device/--/auth/callback');
  const reset = h.calls.find(call => call[0] === 'reset');
  assert.equal(reset[1], 'cook@example.com'); assert.equal(reset[2].redirectTo, confirmation.options.emailRedirectTo);
});

test('expired recovery callbacks cannot leave a normal account in recovery mode', async () => {
  const h = harness({ initial: userSession }); await settle();
  h.auth.setSession = async () => ({ data: {}, error: new Error('Expired link') });
  await assert.rejects(h.render().handleCallback('timpla://auth/callback#access_token=expired&refresh_token=expired&type=recovery'), /Expired link/);
  assert.equal(h.render().recovery, false);
  assert.equal(h.stored.has('timpla.auth.password-recovery'), false);
});
