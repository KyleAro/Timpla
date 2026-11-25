import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';
import { AuthButton, AuthForm, AuthLink } from '../components/AuthForm';

export default function SaveAccount() {
  return <AuthForm title="Save your result" notice="Log in or create an account to keep your scans and recipes.">
    <AuthButton title="Log in" onPress={() => router.push('/login')} />
    <AuthButton title="Create an account" onPress={() => router.push('/sign-up')} />
    <AuthLink title="Keep browsing" onPress={() => { void AsyncStorage.multiRemove(['timpla.pending-scan', 'timpla.pending-recipe']).then(() => router.back()); }} />
  </AuthForm>;
}
