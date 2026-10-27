import { PropsWithChildren, useState } from 'react';
import { ActivityIndicator, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { BrandMark } from './BrandMark';
import { BrandWordmark } from './BrandWordmark';
import { FormIcon } from './FormIcon';
import { useTheme } from '../theme/ThemeContext';

export function AuthForm({ title, subtitle, error, notice, children }: PropsWithChildren<{ title: string; subtitle?: string; error?: string; notice?: string }>) {
  const { palette } = useTheme();
  return <SafeAreaView style={[styles.screen, { backgroundColor: palette.background }]}>
    <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView keyboardShouldPersistTaps="handled" keyboardDismissMode="on-drag" contentContainerStyle={styles.scroll}>
        <View style={styles.content}>
          <View style={styles.brand}><BrandMark size={48} /><BrandWordmark /></View>
          <Text accessibilityRole="header" style={[styles.heading, { color: palette.text }]}>{title}</Text>
          {subtitle ? <Text style={[styles.subtitle, { color: palette.muted }]}>{subtitle}</Text> : null}
          {error ? <Text accessibilityRole="alert" style={[styles.message, { color: palette.error }]}>{error}</Text> : null}
          {notice ? <Text accessibilityLiveRegion="polite" style={[styles.message, { color: palette.muted }]}>{notice}</Text> : null}
          <View style={styles.fields}>{children}</View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  </SafeAreaView>;
}

export function AuthInput({ password, ...props }: TextInputProps & { password?: boolean }) {
  const { palette } = useTheme();
  const [show, setShow] = useState(false);
  const [focused, setFocused] = useState(false);
  return <View style={[styles.field, { backgroundColor: palette.surface, borderColor: focused ? palette.accent : palette.border }]}>
    {password || props.keyboardType === 'email-address' ? <FormIcon name={password ? 'lock' : 'email'} /> : null}
    <TextInput {...props} placeholderTextColor={palette.muted} secureTextEntry={password && !show} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)} style={[styles.input, { color: palette.text }, props.style]} />
    {password ? <Pressable accessibilityRole="button" accessibilityLabel={show ? 'Hide password' : 'Show password'} onPress={() => setShow(!show)} style={styles.eye}><FormIcon name={show ? 'eye-off' : 'eye'} /></Pressable> : null}
  </View>;
}
export function AuthButton({ title, onPress, busy, disabled }: { title: string; onPress: () => void; busy?: boolean; disabled?: boolean }) {
  const { palette } = useTheme();
  return <Pressable accessibilityRole="button" accessibilityState={{ busy, disabled: busy || disabled }} disabled={busy || disabled} onPress={onPress} style={({ pressed }) => [styles.button, { backgroundColor: pressed ? palette.accentPressed : palette.accent, opacity: busy || disabled ? 0.65 : 1 }]}>
    {busy ? <ActivityIndicator color="#FFF8ED" /> : <Text style={styles.buttonText}>{title}</Text>}
  </Pressable>;
}
export function AuthLink({ title, onPress, disabled }: { title: string; onPress: () => void; disabled?: boolean }) {
  const { palette } = useTheme();
  return <Pressable accessibilityRole="button" disabled={disabled} onPress={onPress} style={[styles.link, { opacity: disabled ? 0.5 : 1 }]}><Text style={{ color: palette.accent, fontSize: 14, fontWeight: '600', textAlign: 'center' }}>{title}</Text></Pressable>;
}
const styles = StyleSheet.create({
  screen: { flex: 1 },
  scroll: { flexGrow: 1, justifyContent: 'center', paddingHorizontal: 28, paddingVertical: 36 },
  content: { width: '100%', maxWidth: 400, alignSelf: 'center' },
  brand: { flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'center', gap: 8, marginBottom: 48 },
  heading: { fontSize: 29, fontWeight: '700', letterSpacing: -0.7, marginBottom: 20 },
  subtitle: { fontSize: 15, lineHeight: 23, marginBottom: 22 },
  message: { fontSize: 14, lineHeight: 21, marginBottom: 18 },
  fields: { gap: 16 },
  field: { minHeight: 58, borderWidth: 1, borderRadius: 13, flexDirection: 'row', alignItems: 'center', gap: 12, paddingLeft: 16, paddingRight: 4 },
  input: { flex: 1, minWidth: 0, paddingVertical: 17, paddingRight: 12, fontSize: 16 },
  eye: { minWidth: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' },
  button: { minHeight: 58, borderRadius: 13, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16 },
  buttonText: { color: '#FFF8ED', fontSize: 17, fontWeight: '600' },
  link: { minHeight: 44, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 8 },
});
