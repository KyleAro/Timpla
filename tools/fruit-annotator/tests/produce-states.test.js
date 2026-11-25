import test from 'node:test';
import assert from 'node:assert/strict';
import { withProduceStates } from '../dist/produce-states.js';
import { assignCollectionSplits } from '../dist/core.js';
test('whole and cut produce classes are separate and original IDs are preserved', () => {
  const original = [{ id: 'tomato', name: 'Tomato', exportName: 'tomato', category: 'Vegetables', color: '#123456' }, { id: 'chicken', name: 'Chicken', exportName: 'chicken', category: 'Chicken' }];
  let id = 0; const result = withProduceStates(original, () => `new-${id++}`);
  assert.equal(result.length, 4); assert.equal(result[0].id, 'tomato'); assert.equal(original.length, 2);
  assert.deepEqual(result.filter(x => x.produceParentId === 'tomato').map(x => x.exportName), ['tomato_unsliced', 'tomato_sliced']);
  assert.equal(withProduceStates(result).length, 4);
});
test('existing prepared states are not automatically called whole produce', () => {
  assert.equal(withProduceStates([{ id: 'x', name: 'Chopped tomato', exportName: 'chopped_tomato', category: 'Vegetables' }]).length, 1);
});
test('collection mode exports 100 training and 20 testing per ingredient and respects assignments', () => {
  const items = Array.from({ length: 240 }, (_, i) => ({ id: String(i), hash: String(i).padStart(3, '0'), defaultLabel: i < 120 ? 'tomato_unsliced' : 'tomato_sliced' }));
  const result = assignCollectionSplits(items);
  for (const key of ['tomato_unsliced', 'tomato_sliced']) { const rows = items.filter(item => item.defaultLabel === key); assert.equal(rows.filter(item => result.get(item.id) === 'train').length, 100); assert.equal(rows.filter(item => result.get(item.id) === 'test').length, 20); }
  items[0].datasetSplit = 'test'; assert.equal(assignCollectionSplits(items).get('0'), 'test');
});
