# AdBlocker (Android)

System-wide ad blocker for Android. No root needed.

## How it works
The app starts a local VPN that captures **only DNS lookups** (everything else bypasses it).
When an app asks for the address of an ad server (e.g. `ads.example-network.com`), the app answers
`0.0.0.0`, so the ad never loads. Other lookups are forwarded to Cloudflare (1.1.1.1).
No traffic is routed through any remote server.

## Get the APK
1. Push this repo to GitHub; the **Build APK** workflow (Actions tab) builds it.
   Download the `AdBlocker-debug-apk` artifact and unzip it.
2. Copy `app-debug.apk` to your phone and install it (allow "install unknown apps").

Or build locally with Android Studio: open the `AdBlocker` folder and press Run.

## Use
Open the app → **Turn on** → accept the VPN prompt. Tap **Update ad list** once to download a
large community blocklist (StevenBlack hosts).

## Limits
- Blocks ads served from separate ad domains (most in-app ads). Ads served from the same
  domain as the content (e.g. YouTube's own ads) cannot be blocked with DNS filtering.
- Apps using hard-coded IPs or DNS-over-HTTPS bypass it. Turn off "Private DNS" in Android
  settings if ads still appear.
- IPv4 DNS only; only one VPN can be active at a time on Android.
