export const onboardingKey = 'timpla.onboarding';

export function hasCompletedOnboarding(raw: string | null): boolean {
  if (!raw) return false;
  try {
    const value: unknown = JSON.parse(raw);
    if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
    const record = value as Record<string, unknown>;
    if (record.completed === false) return false;
    // Earlier app versions wrote this complete record only on the final slide.
    return typeof record.name === 'string'
      && Boolean(record.preferences && typeof record.preferences === 'object' && !Array.isArray(record.preferences));
  } catch {
    return false;
  }
}
