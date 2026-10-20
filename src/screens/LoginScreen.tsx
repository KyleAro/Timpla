import { BrandMark } from '../components/BrandMark';
import { useRef, useState } from 'react';
import { Link } from 'expo-router';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FormIcon } from '../components/FormIcon';
import { ThemePalette } from '../theme/colors';
import { useTheme } from '../theme/ThemeContext';

export default function LoginScreen() {
  const { palette } = useTheme();
  const styles = makeStyles(palette);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState<'email' | 'password' | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const passwordRef = useRef<TextInput>(null);

  function submit() {
    setNotice('');
    if (!email.trim() || !password) {
      setError('Enter your email and password.');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError('Enter a valid email address.');
      return;
    }
    setError('');
    // UI milestone only. Never create a pretend authenticated session.
    setNotice('Sign-in is not connected yet. Your details have not been sent or saved.');
  }

  return (
    <SafeAreaView style={styles.screen}>
      <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled" keyboardDismissMode="on-drag">
          <View style={styles.content}>
            <View style={styles.logo}><BrandMark size={112} /></View>
            <Text accessibilityRole="header" style={styles.heading}>Welcome back</Text>
            <View style={styles.fields}>
              <View style={[styles.field, focused === 'email' && styles.focused]}>
                <FormIcon name="email" />
                <TextInput accessibilityLabel="Email address" autoComplete="email" textContentType="emailAddress" keyboardType="email-address" autoCapitalize="none" autoCorrect={false} placeholder="Email" placeholderTextColor={palette.muted} value={email} onChangeText={(value) => { setEmail(value); setError(''); setNotice(''); }} onFocus={() => setFocused('email')} onBlur={() => setFocused(null)} returnKeyType="next" onSubmitEditing={() => passwordRef.current?.focus()} style={styles.input} />
              </View>
              <View style={[styles.field, focused === 'password' && styles.focused]}>
                <FormIcon name="lock" />
                <TextInput ref={passwordRef} accessibilityLabel="Password" autoComplete="current-password" textContentType="password" autoCapitalize="none" autoCorrect={false} secureTextEntry={!showPassword} placeholder="Password" placeholderTextColor={palette.muted} value={password} onChangeText={(value) => { setPassword(value); setError(''); setNotice(''); }} onFocus={() => setFocused('password')} onBlur={() => setFocused(null)} returnKeyType="go" onSubmitEditing={submit} style={styles.input} />
                <Pressable accessibilityRole="button" accessibilityLabel={showPassword ? 'Hide password' : 'Show password'} onPress={() => setShowPassword(!showPassword)} style={styles.eye}>
                  <FormIcon name={showPassword ? 'eye-off' : 'eye'} />
                </Pressable>
              </View>
            </View>
            <Pressable accessibilityRole="button" onPress={() => { setError(''); setNotice('Password reset will be added after account sign-in is connected.'); }} style={styles.forgot}><Text style={styles.link}>Forgot password?</Text></Pressable>
            {error ? <Text accessibilityLiveRegion="polite" style={styles.error}>{error}</Text> : null}
            {notice ? <Text accessibilityLiveRegion="polite" style={styles.notice}>{notice}</Text> : null}
            <Pressable accessibilityRole="button" onPress={submit} style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}><Text style={styles.buttonText}>Log in</Text></Pressable>
            <View style={styles.footer}><Text style={styles.footerText}>New here?</Text><Pressable accessibilityRole="button" onPress={() => { setError(''); setNotice('The sign-up screen is the next step.'); }} style={styles.signup}><Text style={styles.signupText}>Sign up</Text></Pressable></View>
            {__DEV__ && <Link href="/home" replace asChild><Pressable style={styles.preview}><Text style={styles.previewText}>Preview app · skip login</Text></Pressable></Link>}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function makeStyles(p: ThemePalette) {
return StyleSheet.create({
  screen: { flex: 1, backgroundColor: p.background },
  scroll: { flexGrow: 1, justifyContent: 'center', paddingHorizontal: 28, paddingVertical: 36 },
  content: { width: '100%', maxWidth: 400, alignSelf: 'center' },
  logo: { alignItems: 'center', marginBottom: 60 },
  heading: { fontSize: 29, fontWeight: '700', color: p.text, marginBottom: 30, letterSpacing: -0.7 },
  fields: { gap: 16 },
  field: { minHeight: 58, flexDirection: 'row', alignItems: 'center', gap: 12, paddingLeft: 16, paddingRight: 4, borderWidth: 1, borderColor: p.border, borderRadius: 13, backgroundColor: p.surface },
  focused: { borderColor: p.accent },
  input: { flex: 1, minWidth: 0, paddingVertical: 17, fontSize: 16, color: p.text },
  eye: { minWidth: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' },
  forgot: { alignSelf: 'flex-end', minHeight: 48, justifyContent: 'center', marginTop: 4, marginBottom: 20 },
  link: { color: p.accent, fontSize: 14 },
  button: { minHeight: 58, backgroundColor: p.accent, borderRadius: 13, alignItems: 'center', justifyContent: 'center' },
  buttonPressed: { backgroundColor: p.accentPressed },
  buttonText: { color: '#FFFFFF', fontSize: 17, fontWeight: '600' },
  footer: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginTop: 20, gap: 5 },
  footerText: { color: p.text, fontSize: 14 },
  signup: { minHeight: 48, justifyContent: 'center', paddingHorizontal: 3 },
  signupText: { color: p.accent, fontSize: 14, fontWeight: '600' },
  error: { color: p.error, fontSize: 14, lineHeight: 21, marginBottom: 16 },
  notice: { color: p.muted, fontSize: 14, lineHeight: 21, marginBottom: 16 },
  preview: { minHeight: 48, alignItems: 'center', justifyContent: 'center', marginTop: 14 },
  previewText: { color: p.muted, fontSize: 13, textDecorationLine: 'underline' },
});
}


