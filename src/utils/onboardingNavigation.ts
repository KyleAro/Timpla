type Point = { x: number; y: number };

// Form controls opt out before their touches reach this page-level navigation.
export function storyDirection(start: Point | null, end: Point, width: number, blocked: boolean): -1 | 0 | 1 {
  if (!start || blocked) return 0;
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  if (Math.abs(dx) > 65 && Math.abs(dx) > Math.abs(dy) * 1.4) return dx < 0 ? 1 : -1;
  if (Math.abs(dx) < 10 && Math.abs(dy) < 10) {
    if (end.x < width * 0.5) return -1;
    if (end.x > width * 0.5) return 1;
  }
  return 0;
}
