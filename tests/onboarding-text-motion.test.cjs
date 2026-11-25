const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');
const ts = require('../node_modules/typescript');

test('native word reveal waits for layout, springs in, and keeps spaces between words', () => {
  const effects = [];
  const springCalls = [];
  const memo = [];
  const state = [];
  let slot = 0;
  const react = {
    useMemo(create) { const index = slot++; return memo[index] ??= create(); },
    useState(initial) { const index = slot++; state[index] ??= initial; return [state[index], value => { state[index] = value; }]; },
    useEffect(effect) { effects.push(effect); },
  };
  class Value {
    constructor(value) { this.value = value; }
    setValue(value) { this.value = value; }
    interpolate(config) { return config; }
  }
  const native = {
    Animated: {
      Value, Text: 'Animated.Text',
      spring(value, config) { springCalls.push({ value, config }); return { start() {}, stop() {} }; },
      stagger(delay, animations) { return { start() {}, stop() {}, delay, animations }; },
    },
    StyleSheet: { create: value => value },
    View: 'View',
  };
  const jsx = (type, props) => ({ type, props });
  const moduleUnderTest = { exports: {} };
  vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/components/OnboardingSplitText.tsx', 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
  }).outputText, {
    module: moduleUnderTest, exports: moduleUnderTest.exports,
    require(name) {
      if (name === 'react') return react;
      if (name === 'react-native') return native;
      if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx };
      throw new Error(name);
    },
    setTimeout(callback) { callback(); return 1; }, clearTimeout() {},
    requestAnimationFrame(callback) { callback(); return 1; }, cancelAnimationFrame() {},
  });
  const render = () => { slot = 0; effects.length = 0; return moduleUnderTest.exports.OnboardingSplitText({
    text: 'Hi, there.', style: { fontSize: 34 }, reduceMotion: false, heading: true,
  }); };
  const initial = render();
  effects.forEach(effect => effect());
  assert.equal(springCalls.length, 0);
  initial.props.onLayout();
  const laidOut = render();
  effects.forEach(effect => effect());
  assert.equal(springCalls.length, 2);
  assert.equal(springCalls[0].config.useNativeDriver, true);
  assert.ok(laidOut.props.children[0].props.style[1].marginRight > 0);
});
