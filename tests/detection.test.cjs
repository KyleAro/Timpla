const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function load(relative, dependencies, globals = {}) {
  const filename = path.resolve(process.cwd(), relative);
  const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(code, { module, exports: module.exports, Map, Set, Error,
    require(name) { if (name in dependencies) return dependencies[name]; throw Error(`Unexpected import ${name}`); },
    ...globals,
  }, { filename });
  return module.exports;
}
const normalization = load('src/utils/normalizeIngredient.ts', {});
const { scanReducer, initialScanState } = load('src/state/scanHistory.ts', { '../utils/normalizeIngredient': normalization });
const capture = (state, id) => scanReducer(state, { type: 'capture', scan: { id, photo: `${id}.jpg`, createdAt: 1, ingredients: [], selectedDish: null } });
const predicted = [{ name: 'Egg', label: 'egg', confidence: 0.9 }, { name: 'Tomato', label: 'tomato', confidence: 0.8 }];

test('manual additions survive a pending detection and removed predictions stay removed on retry', () => {
  let state = capture(initialScanState, 'a');
  state = scanReducer(state, { type: 'ingredients', names: ['Salt'] });
  state = scanReducer(state, { type: 'detected', id: 'a', ingredients: predicted });
  assert.equal(state.ingredients.join(','), 'Salt,Egg,Tomato');
  state = scanReducer(state, { type: 'ingredients', names: ['Salt', 'Egg'] });
  state = scanReducer(state, { type: 'detected', id: 'a', ingredients: predicted });
  assert.equal(state.ingredients.join(','), 'Salt,Egg');
  assert.equal(state.recentScans[0].ingredients[0].confidence, null);
  assert.equal(state.recentScans[0].ingredients[1].label, 'egg');
});

test('late results cannot change a different active scan or reset account', () => {
  let state = capture(capture(initialScanState, 'a'), 'b');
  assert.equal(scanReducer(state, { type: 'detected', id: 'a', ingredients: predicted }), state);
  state = scanReducer(state, { type: 'reset' });
  assert.equal(scanReducer(state, { type: 'detected', id: 'b', ingredients: predicted }), state);
  assert.equal(state.recentScans.length, 0);
});

function client(fetch) {
  return load('src/services/detection.ts', { 'react-native': { Platform: { OS: 'web' } },
    'expo-file-system': { File: class {} }, 'expo/fetch': { fetch } }, {
    process: { env: { EXPO_PUBLIC_DETECTOR_URL: 'http://localhost:8000/' } }, fetch, FormData, Blob,
  });
}
test('web upload sends the actual photo and deduplicates valid model names by highest confidence', async () => {
  let uploaded;
  const api = client(async (url, options) => {
    if (url === 'blob:photo') return { ok: true, blob: async () => new Blob(['photo'], { type: 'image/jpeg' }) };
    assert.equal(url, 'http://localhost:8000/detect');
    uploaded = options.body.get('image');
    return { ok: true, json: async () => ({ ingredients: [
      { label: 'egg', name: 'egg', confidence: 0.5 }, { label: 'egg', name: 'egg', confidence: 0.9 },
    ] }) };
  });
  const result = await api.detectIngredients('blob:photo', new AbortController().signal);
  assert.equal(await uploaded.text(), 'photo');
  assert.equal(result.length, 1);
  assert.equal(result[0].name, 'Egg');
  assert.equal(result[0].confidence, 0.9);
});

test('invalid detections and failed server responses are surfaced rather than invented', async () => {
  for (const response of [
    { ok: true, json: async () => ({ ingredients: [{ label: 'egg', name: 'egg', confidence: 2 }] }) },
    { ok: false, json: async () => ({ detail: 'Photo is invalid.' }) },
  ]) {
    const api = client(async url => url === 'blob:photo' ? { ok: true, blob: async () => new Blob(['x']) } : response);
    await assert.rejects(api.detectIngredients('blob:photo', new AbortController().signal), /invalid/i);
  }
});

test('phone uploads use Expo File bytes compatible with the installed SDK multipart serializer', async () => {
  const { convertFormDataAsync } = load('node_modules/expo/src/winter/fetch/convertFormData.ts', {
    '../../utils/blobUtils': { blobToArrayBufferAsync: blob => blob.arrayBuffer() },
  }, { Blob, TextEncoder, Uint8Array });
  for (const platform of ['android', 'ios']) {
    const parts = [];
    class NativeFormData {
      append(name, value) { parts.push([name, value]); }
      entries() { return parts; }
    }
    class NativeFile {
      exists = true; size = 16; name = 'photo.heic'; type = 'image/heic';
      constructor(uri) { this.uri = uri; }
      async bytes() { return new TextEncoder().encode('real-photo-bytes'); }
    }
    const controller = new AbortController();
    const expoFetch = async (url, options) => {
        assert.equal(url, 'http://192.168.1.2:8081/timpla-detector/detect');
        assert.equal(options.method, 'POST');
        assert.equal(options.signal, controller.signal);
        assert.equal(options.headers, undefined); // Native fetch must generate the multipart boundary.
        const encoded = await convertFormDataAsync(options.body, 'test-boundary');
        const body = new TextDecoder().decode(encoded.body);
        assert.match(body, /name="image"; filename="photo.heic"/);
        assert.match(body, /content-type: image\/heic/);
        assert.match(body, /real-photo-bytes/);
        return { ok: true, json: async () => ({ ingredients: [] }) };
    };
    const api = load('src/services/detection.ts', {
      'react-native': { Platform: { OS: platform } },
      'expo-file-system': { File: NativeFile }, 'expo/fetch': { fetch: expoFetch },
    }, {
      process: { env: { EXPO_PUBLIC_DETECTOR_URL: 'http://192.168.1.2:8081/timpla-detector' } },
      FormData: NativeFormData,
      fetch: () => assert.fail('Phone uploads must use Expo fetch'),
    });
    const result = await api.detectIngredients('file:///phone/cache/photo.heic', controller.signal);
    assert.equal(result.length, 0);
    assert.equal(parts[0][0], 'image');
    assert.equal(parts[0][1].uri, 'file:///phone/cache/photo.heic');
    assert.equal(parts[0][1].type, 'image/heic');
  }
  await assert.rejects(convertFormDataAsync({ entries: () => [
    ['image', { uri: 'file:///photo.jpg', name: 'photo.jpg', type: 'image/jpeg' }],
  ] }, 'test-boundary'), /Unsupported FormDataPart implementation/);
});

test('browser development uploads through the current Expo origin', async () => {
  const api = load('src/services/detection.ts', { 'react-native': { Platform: { OS: 'web' } },
    'expo-file-system': { File: class {} }, 'expo/fetch': { fetch: () => assert.fail('Web uses browser fetch') } }, {
    __DEV__: true, window: { location: { origin: 'http://localhost:8081' } },
    process: { env: { EXPO_PUBLIC_DETECTOR_URL: 'http://192.168.1.2:8081/timpla-detector' } },
    FormData, Blob,
    fetch: async url => {
      if (url === 'blob:photo') return { ok: true, blob: async () => new Blob(['photo']) };
      assert.equal(url, 'http://localhost:8081/timpla-detector/detect');
      return { ok: true, json: async () => ({ ingredients: [] }) };
    },
  });
  assert.equal((await api.detectIngredients('blob:photo', new AbortController().signal)).length, 0);
});

test('Expo proxy forwards multipart headers locally and explains a stopped detector', () => {
  let options, errorHandler, piped;
  const upstream = {
    setTimeout() {}, destroy() {},
    on(event, handler) { if (event === 'error') errorHandler = handler; },
  };
  const { withDetectorProxy } = load('scripts/detectorProxy.cjs', {
    'node:http': { request(value) { options = value; return upstream; } },
  });
  const response = {
    writeHead(status, headers) { this.status = status; this.headers = headers; },
    end(body) { this.body = body; }, on() {},
  };
  withDetectorProxy(() => assert.fail('Upload must use the detector proxy'))({
    url: '/timpla-detector/detect', method: 'POST',
    headers: { 'content-type': 'multipart/form-data; boundary=test', 'content-length': '123', authorization: 'do-not-forward' },
    on() {}, pipe(destination) { piped = destination; },
  }, response);
  assert.equal(options.hostname, '127.0.0.1');
  assert.equal(options.port, 8000);
  assert.equal(options.path, '/detect');
  assert.equal(options.headers['content-type'], 'multipart/form-data; boundary=test');
  assert.equal(options.headers.authorization, undefined);
  assert.equal(piped, upstream);
  errorHandler(Error('ECONNREFUSED'));
  assert.equal(response.status, 502);
  assert.match(JSON.parse(response.body).detail, /Python detector is unavailable/);
});

test('photo validation waits for callback-based image sizing on web and phone', async () => {
  for (const platform of ['web', 'android', 'ios']) {
    for (const outcome of ['valid', 'failed', 'empty']) {
      let sizeFinished = false;
      const { validatePhoto } = load('src/utils/validatePhoto.ts', {
        'expo-file-system': { File: class { exists = true; size = 100; } },
        'react-native': { Platform: { OS: platform }, Image: {
          getSize(uri, success, failure) {
            assert.equal(typeof success, 'function');
            assert.equal(typeof failure, 'function');
            queueMicrotask(() => {
              sizeFinished = true;
              if (outcome === 'failed') failure(Error('Image decode failed'));
              else success(outcome === 'empty' ? 0 : 640, 480);
            });
            // Matches the web API: no Promise is returned.
          },
        } },
      }, { fetch: async () => ({ ok: true, blob: async () => ({ size: 100, type: 'image/jpeg' }) }) });
      const validation = validatePhoto('photo.jpg', 'image', 'image/jpeg');
      if (outcome === 'valid') await validation;
      else await assert.rejects(validation, /Choose a valid image/);
      assert.equal(sizeFinished, true);
    }
  }
});
