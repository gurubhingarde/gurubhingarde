# Baby Bubble Party 🫧

A no-rules, can't-lose tapping game for toddlers, starring your own child.

- Bubbles float up with her face or animals inside: tap to **pop** (silly sounds, confetti, her face boings out).
- Tap the little girl in the saree: she **jumps**, spins and shouts "wheee!".
- Tap the **sun** (it has her face too) to make it spin and giggle.
- Her face **peeks** in from the side of the screen: tap it for a surprise.
- Every 10 pops: a **party** with a rainbow, fanfare and confetti rain.
- Tap anywhere else: sparkles and she toddles over.

There's no text, no score and no way to fail. The back button does nothing, so tiny hands can't leave the app by accident.

## Parents' corner

**Press and hold the faint gear (top left) for 2 seconds.** From there you can:

- pick 3 photos (normal / surprised / shouting face) from the phone gallery and drag them into the oval
- turn sounds on or off
- exit the app

Photos are saved only on the phone. **No photos are stored in this repository.**

## Getting the APK

Every push that touches `baby-game/` runs the GitHub Action **Build Baby Bubble Party APK**.
Open the run on the repo's *Actions* tab, download the `BabyBubbleParty-apk` artifact, unzip it and
install `app-debug.apk` on the phone (allow "install unknown apps" when asked).

Building locally works too: `cd baby-game && ./gradlew assembleDebug` (needs the Android SDK).

## Baking photos in (optional, stays off git)

```sh
# one HTML file you can open on any phone
python3 tools/bundle_faces.py --calm calm.jpg --oh surprised.jpg --yell shouting.jpg -o ~/baby-bubble-party.html

# or copy the faces into the app assets for a local APK build (git-ignored)
python3 tools/bundle_faces.py --calm calm.jpg --oh surprised.jpg --yell shouting.jpg --assets
```

## Layout

- `app/src/main/assets/index.html`: the whole game (HTML canvas plus synthesized Web Audio sounds, no other assets)
- `app/src/main/java/.../MainActivity.java`: full-screen WebView wrapper with a gallery photo picker
- `tools/bundle_faces.py`: puts face photos into a standalone HTML file or into the APK assets
