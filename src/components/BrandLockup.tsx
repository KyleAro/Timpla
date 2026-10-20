import { BrandMark } from './BrandMark';

// Compatibility wrapper: all app branding uses the same approved artwork.
export function BrandLockup() {
  return <BrandMark size={52} />;
}
