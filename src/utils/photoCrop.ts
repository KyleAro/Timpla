export type CaptureFrame = { viewport: { width: number; height: number }; rect: { x: number; y: number; width: number; height: number } };

// Camera preview fills its view with a centered cover fit. Convert the measured
// guide from preview points to the processed photo's pixel coordinates.
export function photoCrop(frame: CaptureFrame, image: { width: number; height: number }) {
  const { viewport, rect } = frame;
  if (![viewport.width, viewport.height, rect.width, rect.height, image.width, image.height].every((value) => Number.isFinite(value) && value > 0) || !Number.isFinite(rect.x) || !Number.isFinite(rect.y)) throw new Error('Invalid capture dimensions');
  const scale = Math.max(viewport.width / image.width, viewport.height / image.height);
  const offsetX = (image.width * scale - viewport.width) / 2;
  const offsetY = (image.height * scale - viewport.height) / 2;
  const left = Math.max(0, Math.min(viewport.width, rect.x));
  const top = Math.max(0, Math.min(viewport.height, rect.y));
  const right = Math.max(0, Math.min(viewport.width, rect.x + rect.width));
  const bottom = Math.max(0, Math.min(viewport.height, rect.y + rect.height));
  if (right <= left || bottom <= top) throw new Error('Capture guide is outside the preview');
  const originX = Math.min(image.width - 1, Math.max(0, Math.round((left + offsetX) / scale)));
  const originY = Math.min(image.height - 1, Math.max(0, Math.round((top + offsetY) / scale)));
  const width = Math.min(image.width - originX, Math.max(1, Math.round((right - left) / scale)));
  const height = Math.min(image.height - originY, Math.max(1, Math.round((bottom - top) / scale)));
  return { originX, originY, width, height };
}

export function captureMask(frame: CaptureFrame, radius = 20) {
  const { viewport, rect: { x, y, width, height } } = frame;
  const r = Math.min(radius, width / 2, height / 2);
  return `M0 0H${viewport.width}V${viewport.height}H0Z M${x + r} ${y}H${x + width - r}Q${x + width} ${y} ${x + width} ${y + r}V${y + height - r}Q${x + width} ${y + height} ${x + width - r} ${y + height}H${x + r}Q${x} ${y + height} ${x} ${y + height - r}V${y + r}Q${x} ${y} ${x + r} ${y}Z`;
}
