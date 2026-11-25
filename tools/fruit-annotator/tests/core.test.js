import test from 'node:test';
import assert from 'node:assert/strict';
import { assignSplits, validBox, yoloLines } from '../dist/core.js';
import { ZipWriter, readBackupZip } from '../dist/zip.js';
const labels = [{ id: 'mango' }, { id: 'banana' }];
test('YOLO export normalizes centers, uses current class mapping, rejects invalid boxes', () => {
  const entry = { name: 'fruit.jpg', boxes: [{ labelId: 'banana', x: 0.1, y: 0.2, w: 0.4, h: 0.6 }] };
  assert.equal(yoloLines(entry, labels), '1 0.300000 0.500000 0.400000 0.600000\n');
  assert.equal(yoloLines({ boxes: [] }, labels), '');
  assert.equal(validBox({ labelId: 'removed', x: 0, y: 0, w: 1, h: 1 }, labels), false);
  assert.throws(() => yoloLines({ ...entry, boxes: [{ ...entry.boxes[0], x: 0.8 }] }, labels), /Invalid box/);
});
test('split allocation is deterministic and accounts for every reviewed image', () => {
  const entries = Array.from({ length: 10 }, (_, i) => ({ id: String(i), hash: String(10 - i) }));
  const first = assignSplits(entries, [70, 20, 10]), second = assignSplits([...entries].reverse(), [70, 20, 10]);
  assert.deepEqual([...first], [...second]);
  assert.equal([...first.values()].filter(x => x === 'train').length, 7);
  assert.equal([...first.values()].filter(x => x === 'val').length, 2);
  assert.equal([...first.values()].filter(x => x === 'test').length, 1);
  assert.equal(assignSplits([{ id: 'single' }], [10, 90, 0]).get('single'), 'train');
  assert.throws(() => assignSplits(entries, [70, 30, 10]), /total/);
});
test('streamed ZIP preserves binary originals and backup metadata', async () => {
  const parts = []; let closed = false;
  const writer = new ZipWriter({ write: async bytes => parts.push(bytes), close: async () => { closed = true; } });
  const bytes = new Uint8Array([0, 128, 255, 1, 10]);
  await writer.add('images/train/original.png', new Blob([bytes]));
  await writer.add('labels/train/original.txt', '0 0.5 0.5 1 1\n');
  await writer.add('timpla-project.json', JSON.stringify({ version: 1 }));
  await writer.close(); assert.equal(closed, true);
  const entries = await readBackupZip(new Blob(parts));
  assert.deepEqual(new Uint8Array(await entries.get('images/train/original.png').arrayBuffer()), bytes);
  assert.equal(await entries.get('labels/train/original.txt').text(), '0 0.5 0.5 1 1\n');
  assert.deepEqual(JSON.parse(await entries.get('timpla-project.json').text()), { version: 1 });
});
test('invalid backups fail clearly', async () => {
  await assert.rejects(readBackupZip(new Blob(['not a zip'])), /not a ZIP/);
});
