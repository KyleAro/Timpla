# Android offline demo

The configured installable Android build bundles `assets/models/ingredients_68.onnx` (68 ingredient classes, including vegetables, chicken, beef, pork, and seafood). Camera and gallery photos are set up to resize on the phone, run through ONNX Runtime on the phone, and reach the Results screen without the detector server. Recipe matches use `src/data/offlineRecipeCatalog.json` on Android. Match percentages count listed recipe ingredients found in the scanned or edited inventory; they are not model confidence.

This is a converted copy of `models/ingredient_detector/YOLOv8n_merged_best.pt`. Its exact training provenance and held-out accuracy are not verified. The local recipe catalog is a draft; its ranking uses a simple ingredient coverage score and has not been validated for recommendation quality. Unknown allergy categories and diets without verified labels return no matches. Always review recipe and package labels when allergies matter.

## Build and test

For development in VS Code, start an Android emulator, then run `npm start` and `npm run android` in the project folder. `npm run android` creates and installs the app's native Android build. `npm start` starts Metro; it can also be started automatically by the Android command. Expo Go cannot run the ONNX native module.

For an offline APK, run `npm run android:offline` with an emulator or phone connected. This makes a release build with the JavaScript bundle and model inside the app, so Metro is not needed when it runs. The APK is produced at `android/app/build/outputs/apk/release/app-release.apk`. Alternatively, `npx eas-cli@latest build --platform android --profile offlineDemo` builds in Expo's cloud and uploads the project to Expo.

1. Create and install the Android release APK using one of those build commands.
2. Install the resulting APK on the Android phone while a connection is available. Open the app, finish onboarding in guest mode, and grant camera access.
3. Turn on airplane mode. Force close and reopen the app, then take a photo and upload a gallery photo. Confirm detected ingredients, boxes, and recipe match percentages. Edit the ingredient list and check that matches update. Restart once more in airplane mode to check cold startup.
4. The guest flow covers scanning and recipe matches. Saving a result currently asks the guest to sign in, so use an already signed-in account only when its profile has been confirmed to load offline. Account registration, sign-in, cloud sync, and other server-only features still require internet.

The Android JavaScript export confirms the ONNX file is included, and local recipe filtering has automated tests. The native ONNX session, camera performance, and complete airplane mode flow still need a test on the actual Android APK before the defense.
