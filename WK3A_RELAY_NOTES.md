# WK3A Relay — Local Control via Tasmota (Project Notes)

## Goal
Control a 3-channel WK3A WiFi relay board (currently running an unidentified "VS602 G3" WiFi module, likely bound to eWeLink's cloud service) locally, with no cloud dependency, by replacing the WiFi module with a known ESP8266 and flashing it with Tasmota.

## Background / decision history

* Originally planned to use the official eWeLink Cloud API with a custom Android app (Kotlin + Jetpack Compose scaffold was built — see `WK3ARelayControl.zip` from earlier in this project).
* Considered reverse-engineering eWeLink's local LAN protocol (AES-encrypted local HTTP + mDNS) — documented by the community (SonoffLAN / ewelink-api-next), but still requires a one-time cloud key extraction.
* Decided approach: swap the unidentified VS602 module for a known ESP8266, flash with Tasmota, and control it purely over the local network. Avoids cloud dependency and developer-account approval entirely.

## Hardware in hand

* WK3A relay board — 3× Songle SRD-05VDC-SL-C relays, screw terminals, 7–32V input, onboard 3.3V/5V regulation. Original WiFi module (VS602 G3) could not be positively identified (chip marking illegible/obscured).
* Replacement WiFi module — confirmed ESP8266EX (Espressif, clearly marked) with a Puya P25Q80H flash chip. ESP-01 form factor breakout with labeled pins: `3V3, RST, EN, TXD` / `GND, IO2, IO0, RXD`.
* USB programmer — "FT232 WIFI Module Adapter... for ESP8266 ESP-01/01S" (Robu.in SKU R224624, ₹76). Actual onboard chip appears to be CH340/CP2102 despite "FT232" in the listing title. Has a physical flash/run mode switch (unlabeled — determine position by trial).
* Test unit ordered: a pre-built single-channel ESP8266 WiFi relay module (Robu.in, ~₹226) to validate the full flash → pair → control workflow on simpler, fully-wired hardware before modifying the real 3-relay board.

## Known constraint: ESP-01 GPIO limits
ESP-01 only exposes GPIO0 and GPIO2 as "free" pins. To drive all 3 relay channels, TXD (GPIO1) and RXD (GPIO3) must also be repurposed as outputs in Tasmota. Tradeoffs:

* Serial console/logging is lost after flashing (expected, not a bug).
* No GPIOs left over for the manual buttons (K1/K2/K3) or a status LED.

## Step-by-step plan

### Phase 1 — Validate with the single-relay test module

1. Identify flash-mode trigger (button/jumper, likely GPIO0-to-GND).
2. Install CH340 or CP2102 driver on PC as needed (check Device Manager → Ports; look for "USB-SERIAL CH340" or similar; install driver, replug).
3. Flash with [Tasmotizer](https://github.com/tasmota/tasmotizer) or https://web.esphome.io (Chrome/Edge only — needs WebSerial). Use `tasmota-lite.bin` for a simple relay build.
4. Configure Tasmota module type + relay GPIO in the web UI (Configure → Configure Module) — likely GPIO12 or GPIO13 for relay on this board; confirm by testing live in the UI.
5. Confirm WiFi pairing flow:
   * Device boots, broadcasts `tasmota-XXXXXX` AP.
   * Join that AP from phone, submit home WiFi SSID/password via captive portal (or `192.168.4.1`).
   * Device reboots onto home WiFi; find its IP via router's connected devices list; reserve a static IP for it in the router if possible.
   * Confirm relay toggles from `http://<device-ip>` in a phone browser.

### Phase 2 — Apply to the real WK3A 3-relay board

1. Power off completely; disconnect from mains/supply.
2. Desolder the old VS602 module from its castellated pads.
3. With the board unpowered, use a multimeter (continuity mode) to trace each relay driver's control-signal pad back to the old module's footprint — these become REL1_IN / REL2_IN / REL3_IN.
4. Wire power: board's 3.3V + GND → new ESP-01 module's VCC/EN and GND.
5. Wire signals:
   * GPIO0 → REL1_IN
   * GPIO2 → REL2_IN
   * TXD (GPIO1) → REL3_IN
6. Boot-strap check: GPIO0 and GPIO2 must read HIGH at power-on. Reuse any existing pull-up resistors from the old module's footprint if present; otherwise add 10kΩ pull-ups to 3.3V on each line.
7. Flash Tasmota exactly as in Phase 1, but assign:
   * GPIO0 → Relay1
   * GPIO2 → Relay2
   * GPIO1 (TX) → Relay3 (expect a "losing serial" warning — fine)
8. Test each relay channel individually, powered but with no mains load connected, before wiring into the actual application.

## Phone / app control options (post-flash)

1. Browser bookmark to `http://<device-ip>` — zero setup, works immediately (Tasmota's built-in web UI).
2. Community Tasmota Android apps (Play Store) — nicer UI, still local.
3. Home Assistant — auto-discovers Tasmota devices, adds scheduling, automations, and voice control (Google/Alexa) via its own app.
4. Custom Android app (previously scaffolded for eWeLink) can be repointed to Tasmota's simple local HTTP API instead of eWeLink's cloud API — much simpler, no auth/signing required:

```
GET http://<device-ip>/cm?cmnd=Power1%20TOGGLE
GET http://<device-ip>/cm?cmnd=Power2%20ON
GET http://<device-ip>/cm?cmnd=Power3%20OFF
```

## Open items / things to verify

* [ ] Confirm actual USB-serial chip on the programmer board (CH340 vs CP2102) and install the matching driver.
* [ ] Determine flash-mode switch position by trial (no labels visible).
* [ ] Confirm relay GPIO assignment on the single-relay test module.
* [ ] After desoldering VS602: confirm which 3 pads are the relay control lines via continuity testing.
* [ ] Confirm presence/absence of existing pull-up resistors on GPIO0/GPIO2 signal paths before deciding whether to add new ones.
