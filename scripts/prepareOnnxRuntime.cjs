// onnxruntime-react-native 1.24.3 needs two Expo/Gradle compatibility fixes.
// Remove this script when an upstream npm release includes both fixes.
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..', 'node_modules', 'onnxruntime-react-native');
if (!fs.existsSync(root)) process.exit(0);
const version = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8')).version;
if (version !== '1.24.3') throw new Error(`Review ONNX Runtime patches for version ${version}`);

const gradlePath = path.join(root, 'android', 'build.gradle');
const before = 'if (VersionNumber.parse(REACT_NATIVE_VERSION) < VersionNumber.parse("0.71")) {';
const after = 'def rnVersionParts = REACT_NATIVE_VERSION.split("\\\\.")\n  if (rnVersionParts[0].toInteger() == 0 && rnVersionParts[1].toInteger() < 71) {';
const gradle = fs.readFileSync(gradlePath, 'utf8');
if (gradle.includes(before)) fs.writeFileSync(gradlePath, gradle.replace(before, after));
else if (!gradle.includes(after)) throw new Error('ONNX Runtime Gradle file changed; review patch');

const unimodule = path.join(root, 'unimodule.json');
if (fs.existsSync(unimodule)) fs.unlinkSync(unimodule);
console.log('Prepared ONNX Runtime for Expo Android autolinking and Gradle 9.');
