const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');
const ts = require('../node_modules/typescript');

function slider({ disabled = false, width = 320 } = {}) {
  let gestures;
  let calls = 0;
  let state = 0;
  class Value {
    constructor(value) { this.value = value; }
    setValue(value) { this.value = value; }
    stopAnimation() {}
  }
  const effects = [];
  const react = {
    useState(initial) {
      const value = state++ === 0 ? width : typeof initial === 'function' ? initial() : initial;
      return [value, () => {}];
    },
    useRef: value => ({ current: value }),
    useMemo: create => create(),
    useEffect: effect => effects.push(effect),
  };
  const native = {
    AccessibilityInfo: {
      isScreenReaderEnabled: () => Promise.resolve(false),
      addEventListener: () => ({ remove() {} }),
    },
    Animated: {
      Value, View: 'Animated.View',
      timing: (value, config) => ({ start: () => value.setValue(config.toValue) }),
    },
    PanResponder: { create: handlers => { gestures = handlers; return { panHandlers: {} }; } },
    Platform: { OS: 'ios' },
    Pressable: 'Pressable', Text: 'Text',
    StyleSheet: { create: styles => styles },
  };
  const jsx = (type, props) => ({ type, props });
  const module = { exports: {} };
  const source = ts.transpileModule(fs.readFileSync('src/components/SlideToContinue.tsx', 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  vm.runInNewContext(source, {
    module, exports: module.exports,
    require(name) {
      if (name === '../theme/tokens') return { typography: { body: 16 } };
      if (name === 'react') return react;
      if (name === 'react-native') return native;
      if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx };
      if (name.includes('ThemeContext')) return { useTheme: () => ({ palette: {} }) };
      throw new Error(name);
    },
  });
  const view = module.exports.SlideToContinue({
    label: 'Slide to continue', disabled, reduceMotion: false, onComplete: () => calls++,
  });
  effects.forEach(effect => effect());
  return { gestures, view, calls: () => calls };
}

test('short or cancelled slides do not advance, a full slide advances once', () => {
  const control = slider();
  control.gestures.onPanResponderRelease(null, { dx: 80 });
  assert.equal(control.calls(), 0);
  control.gestures.onPanResponderTerminate();
  assert.equal(control.calls(), 0);
  control.gestures.onPanResponderRelease(null, { dx: 250 });
  control.gestures.onPanResponderRelease(null, { dx: 250 });
  assert.equal(control.calls(), 1);
});

test('disabled and not-yet-measured controls cannot advance by sliding', () => {
  for (const control of [slider({ disabled: true }), slider({ width: 0 })]) {
    control.gestures.onPanResponderRelease(null, { dx: 500 });
    assert.equal(control.calls(), 0);
  }
});

test('screen-reader activation advances without dragging and prevents duplicate completion', () => {
  const control = slider();
  control.view.props.onAccessibilityTap();
  control.view.props.onAccessibilityTap();
  assert.equal(control.calls(), 1);
  assert.equal(control.view.props.accessibilityLabel, 'Slide to continue');
});
