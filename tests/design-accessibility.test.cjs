const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('../node_modules/typescript');
const paletteModule = { exports: {} };
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/theme/colors.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { exports: paletteModule.exports, module: paletteModule });
const { themes } = paletteModule.exports;
function luminance(hex) {
  const parts = hex.replace('#', '').match(/../g).map(part => {
    const value = parseInt(part, 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return parts[0] * .2126 + parts[1] * .7152 + parts[2] * .0722;
}
function contrast(a, b) {
  const x = luminance(a), y = luminance(b);
  return (Math.max(x, y) + .05) / (Math.min(x, y) + .05);
}
for (const [mode, p] of Object.entries(themes)) {
  test(mode + ' text and link colors meet normal-text contrast', () => {
    for (const surface of ['background', 'surface', 'secondary']) {
      for (const ink of ['text', 'muted', 'accent', 'error']) {
        const ratio = contrast(p[ink], p[surface]);
        assert.ok(ratio >= 4.5, mode + ' ' + ink + '/' + surface + ' ' + ratio.toFixed(2));
      }
    }
    assert.ok(contrast(p.oliveText, p.olive) >= 4.5);
    assert.ok(contrast(p.profileText, p.profile) >= 4.5);
  });
  test(mode + ' button labels and input boundaries retain contrast', () => {
    assert.ok(contrast('#FFF8ED', p.buttonBackground) >= 4.5);
    assert.ok(contrast('#FFF8ED', p.buttonPressed) >= 4.5);
    assert.ok(contrast(p.border, p.surface) >= 3);
  });
}
