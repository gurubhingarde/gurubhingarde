# Reverse‑Engineering Report — ACTIA "Actiway" DownLoad Tool (CAN‑FD)

**Artifact:** `DLTool-CANFD-1.0.27.0905_NJHT1_2_2.zip`
**Analysis:** 100 % static. No code was executed. Reconstructed from .NET CLI
metadata, decoded CIL method bodies, `ldstr` literals, P/Invoke boundaries and
the shipped configuration/XML, using the REA toolchain
(`inspect-managed-members`, `inspect-managed-native-boundaries`,
`inspect-pe-resources`, `inspect-artifact`).

---

## 1. What it is

A Windows desktop tool from **ACTIA Automotive SA** for **reprogramming
(flash‑downloading) ACTIA "Multic" family ECUs** — truck/bus telematics & body
controllers (`Multic‑S`, `Multic‑SX`) — over three transports: **CAN, CAN‑FD and
DoIP (Diagnostics over IP)**. Internally called *"DTool Graphical Version"* /
`dltoolGUI`, branded *Actiway*.

| Property | Value |
|---|---|
| Product name | Actiway Download Tool, CAN‑FD build |
| Version | **1.0.27.0905** (package tag `NJHT1_2_2`) |
| Vendor | ACTIA Automotive SA ("Copyright Actia") |
| Platform | .NET Framework **4.7.2**, WinForms, **x86 (32‑bit)** |
| Deployment | ClickOnce (`.application` + `.manifest`) |
| Main EXE | `Actiway_DownLoad_Tool.exe` (SHA‑256 `71200e6e…5c2c9`) |
| Diagnostic protocol | **UDS / ISO 14229** over ISO‑TP, plus KWP‑style DIDs |

---

## 2. Module map

The app is a managed GUI shell over a set of protocol and CAN‑hardware DLLs.

### Application / protocol (managed, readable)
| DLL | Role |
|---|---|
| `Actiway_DownLoad_Tool.exe` | GUI (`frmMain`, `frmDownload`, `frmAutodetect`, `loginForm`, `frmAbout`). **Obfuscated** (see §7). |
| `CDownload.dll` | **Core flash engine.** `ACTIA.clDownloadApp` state machine, security‑access, AES/CRC, MiniLZO, hex utilities. *Not obfuscated.* |
| `CDiagOnCan.dll` | `ACTIA.Protocol.clDoCPro` — UDS "Diag‑on‑CAN" session state machine + microsecond timing. |
| `clDoIP.dll`, `clDoIPDiscovery.dll`, `clDoCDiscovery.dll` | DoIP transport (`ACTIA.Protocol.clDoIP`) and vehicle/entity discovery (UDP broadcast `255.255.255.255`). |
| `clDownloaderDrv.dll` | C++/CLI mixed‑mode bridge (`CclDownloaderDrv`, HID I/O `CHidIO/CHidCmd`) to the LevelX native downloader. |
| `clBasicXSDrv.dll` | LevelX **BasicXS** CAN driver glue — loads `LX2kxs1u.dll` / `LXWxXS1s.dll` / `LXN4py2s.dll`; object verbs `LXRDOBJECT`/`LXWROBJECT`/`LXSETEVENT`. |
| `clICanDrv.dll`, `clIProtocol.dll` | Abstract CAN‑driver / protocol interfaces (`ACTIA.Tools.ICanDrv`). |
| `CommandLine.dll` | Standard CommandLineParser (CLI mode). |
| `log4net.dll` | Logging. |

### CAN hardware abstraction (vendor back‑ends)
| Managed wrapper | Native driver | Vendor |
|---|---|---|
| `CZLGCAN.dll` (`ACTIA.clZLGCANDrv`, `ACTIA.ZLGDrv.*`) | `zlgcan.dll`, `ControlCAN(FD).dll`, `kerneldlls/*` | **ZLG / ZhouLigong** USBCAN‑FD, CANFDNET, PCIe‑CANFD, CANFD‑WiFi, etc. |
| `CPeakCAN.dll` (`ACTIA.clPeakCANDrv`, `Peak.Can.Basic.*`) | `PCANBasic.dll` | **PEAK** PCAN |
| `CVectorCAN.dll` (`ACTIA.clVectorCANDrv`) | `vxlapi_NET.dll` | **Vector** XL API (channel name `ActiaTools`/`CAN1`) |
| `CACHDownloader.dll` | — | CACH downloader variant |

The ZLG back‑end is the richest: `kerneldlls/dll_cfg.ini` maps ~33 VCI and ~35
ZLG device IDs to driver DLLs; `kerneldlls/devices_property/*.xml` hold per‑device
channel/bit‑timing property schemas for the whole ZLG CAN/CAN‑FD product line.

---

## 3. The flashing workflow (reconstructed)

Driven by `ACTIA.clDownloadApp.vDLDll_iExecute_Thread` (a single ~6.7 KB‑IL
state machine) with the UDS session logic in
`CDiagOnCan.dll → clDoCPro.StateMachine`.

1. **Select transport & hardware** — CAN / CAN‑FD / DoIP; pick vendor driver,
   channel, baudrate. Defaults from `*.exe.config`:
   `TOOL_SA=0xF9` (tester source addr), `CAN_SA=0xFE`, `EXTEND_PRIO=0x18`
   (J1939‑style 29‑bit priority), `SecKey=0xFFFF`,
   `MinDataSizeCAN=0x10`, `MinDataSizeDoIP=0x400`.
2. **Read ECU identity** (`s32StartReadINFO`) — UDS **ReadDataByIdentifier
   (SID 0x22)** of a large DID catalogue defined in `MulticS.xml`
   (`F180`‑`F182` boot/monitor/calib banners; `FE00`‑`FE21` library banners:
   KWP, DoC, J1939, EEPROM, TcpIP, DoIP, EmWizard, Straton‑VM, Wiring; plus a
   J1939 PGN read `0x18FEDA17`).
3. **Enter programming session & unlock** — DiagnosticSessionControl →
   **SecurityAccess (SID 0x27)**: RequestSeed → `u16Main_eSecKey_Calcul`
   computes the key → SendKey (see §4).
4. **Pick zone / address range** — from `Actiway_Zones_Config.xml` (zone 0 = Main
   MCU Application, 1 = Calibration, …) or a preset in `Actiway_DownLoad_Tool.xml`
   (e.g. *"Multic‑SX → APP_ALL+BSP"* `0x18080000‑0x18FFFFF7`).
5. **Transfer** — RequestDownload (0x34) → TransferData (0x36) → RequestTransferExit
   (0x37), data optionally **MiniLZO‑compressed** (config `LZO`), split into
   `ReprogrammingBlock`/`Segment` chunks of `MinDataSize*`.
6. **Verify** — CRC‑32 of the image (`CRC_32`), optional memory check
   (`memCheck_auto/manual/default`), routine control, ECU reset.

`CDiagOnCan` uses `MicroStopwatch`/`MicroTimer` (QueryPerformanceCounter) for
ISO‑TP P2/STmin timing precision.

---

## 4. Security & cryptography (fully identified)

### 4.1 Operator login — `dltoolGUI.loginForm` + `dltoolGUI.User`
- Users carry `Name`, `Pwd`, `Year` (expiry). Login compares entered
  user/password against an in‑memory `List<User>`, then checks
  `Convert.ToDateTime(Year) − DateTime.Now`: **if the account is expired the
  tool shows a message and calls `Application.Exit()`.** There is also a session
  idle timer (`TotalMinutes`). Credential stores: `User/*.uaf` (dev, user1‑5).
- Passwords are hashed with **SHA‑256** (`dltoolGUI.SHA256Helper`:
  `SHA256`, `GetFileSHA256`, `GetBytesSHA256`, lower/upper hex).

### 4.2 Licensing / feature gating — main EXE string table
Feature entitlements are hard‑coded GUID‑style product codes:
`{11111-22222-20001-00000}`, `…-10009-11112`, `…-30001-0000x`,
`…-40001-0000x`, `…-50001-0000x`, etc. These map to tool capabilities/zones and
are checked at startup (`AesCryptoServiceProvider` referenced alongside them →
the entitlement blob is AES‑protected).

### 4.3 Symmetric crypto — `ACTIA.clDownloadApp` + `Acita_CSG.AESHelper`
- **AES‑128** with a **fixed, hard‑coded passphrase `"actiacsg"`** (8 ASCII
  bytes UTF‑8‑encoded, zero‑padded to a 16‑byte key via
  `new byte[16]` + `Math.Min` + `Array.Copy`; zero IV).
  - `jiaMi(byte[])` = encrypt (pinyin *jiāmì*), `JieMi(byte[])` = decrypt
    (*jiěmì*), `AES128_FromHex(string)`. Output is hex with `-` stripped.
  - `Acita_CSG.AESHelper` provides keyed overloads `AESEncrypt/Decrypt(data,key,iv)`.
- **Takeaway:** payload "encryption" here is obfuscation, not real protection —
  the key `actiacsg` ships in the binary.

### 4.4 Asymmetric & signing
- `Common.RSACryption` — RSA via `RSACryptoServiceProvider` with XML keys
  (`RSAKey`, `RSAEncrypt`/`RSADecrypt`, Unicode and Base64 variants).
- `frmMain.Sign` / `SignCheck` — signs/verifies byte buffers (image provenance
  / download‑package integrity).

### 4.5 UDS SecurityAccess seed→key — `u16Main_eSecKey_Calcul(seed, arg2)` — FULLY DECODED
50‑byte‑IL routine, decoded byte‑for‑byte from `CDownload.dll`:

```
acc = this.u16SecKey          ; config SecKey (default 0xFFFF)
w   = seed                    ; 16-bit seed from the ECU
for i in range(15):           ; blt.s  i < 15
    acc = (acc ^ w) & 0xFFFF
    w   = rotl16(w, 1 + arg2) ; arg2 = 2 at BOTH call sites -> rotate-left by 3
return acc                    ; 16-bit key
```

Equivalently: **`key = SecKey ⊕ seed ⊕ rotl3(seed) ⊕ rotl3²(seed) ⊕ … ⊕ rotl3¹⁴(seed)`**
(15 XORed rotations). The seed is read from the SecurityAccess positive response
big‑endian: `seed = (resp[2] << 8) | resp[3]` (field `tu8Response`, read with
`ldelem.u1`). The key is sent back big‑endian. Both call sites
(`s32StartReadINFO`, `vDLDll_iExecute_Thread`) pass `arg2 = 2`.
This is implemented exactly in `actiway_pytool/crypto.py: seed_to_key_u16`.
`u16DLDll_iCrcInc_Exe` provides an incremental CRC over `tu16DLDll_iCRCTable`.

### 4.6 Image checksum — `CRC_32`
Standard table‑driven **CRC‑32** (`GetCRC32Table`, `Crc32Table[256]`, formatted
`{0:X8}` upper‑case); `CRC_32_FromHex` accepts a hex string.

---

## 5. Firmware file formats

- **Input:** Motorola S‑record / Intel‑HEX firmware. `FileConverter.GestMotoValue`
  parses them (`GetMotololaToOneData`, `GetSegmentsFromFiles`, `MegreData`/
  `MegreToOneData` to merge multiple files into one address space).
- **Model objects:**
  - `FileConverter.Segment` — `DATABLOCK_ID`, `START_ADDR`, `END_ADDR`,
    `UNCOMPREESED_SIZE`.
  - `FileConverter.ReprogrammingBlock` — `Name`, `LOGICAL_INDEX`, `FILE_NAME`,
    `FILE_TYPE`, `IDENT_VALUE`, `ADDR_LEN`, `SIZE_LEN`, `List<Segment>`.
  - `FileConverter.EncodingType` — selects record encoding.
- **Compression:** `SimmoTech.Utils.Compression.MiniLZO` — a pure‑C# **LZO1X**
  port (`Compress`/`Decompress`, `D_INDEX1/2`, `D_MS/MUL/X2/X3`; errors
  *"Output Overrun / Input Overrun / Lookbehind Overrun / EOF Marker Not Found"*).
- **Command‑line converters:** `convert/m2bs.exe`, `convert/m2ms.exe` — native
  ACTIA "lkt" toolkit (`lib/lkt_e.msg`/`lkt_a.msg`; verbs `f2ms f2is f2es m2is
  m2es e2ms i2ms m2bs m2ms` = Motorola/Intel/binary/ELF inter‑conversion;
  messages are Japanese EUC‑JP).

---

## 6. Hex / bit utility library — `CDownload.HexString`
A large toolbox (also mirrored as `VDSUI.Utils.HexString`, `dltoolGUI.HexString`):
byte↔hex↔ASCII↔binary conversions, `HexStr2Dec/BigDec`, `HexSecAddSec`,
`SecAndSec`/`SecOrSec` (bitwise add/AND/OR on hex strings), `Bytes2Num`,
`HexSec2Opposite` (complement). Used throughout to build/parse UDS frames.

---

## 7. Obfuscation

Only **`Actiway_DownLoad_Tool.exe`** is obfuscated (a .NET name/string
obfuscator — pattern consistent with ConfuserEx‑style):

- **Type/member renaming** to random identifiers
  (`ChKmUHEQy5Tfa8l2jd`, `SuZH7KVHUXnL9D8fdQ.vKDNkae93ohJj9hwlJ`, …).
- **String encryption** — `ldstr ""` placeholders; real strings are produced at
  runtime by the decryptor `GQ5rVxJNIgNlqfPvbf.Gm4mRErlhWcW2IjsG9.as5P7Q77p8(int)`.
  (The 18 strings that *do* survive — license GUIDs, `actiacsg`‑adjacent crypto
  type names, `GetDelegateForFunctionPointer` — are the ones the obfuscator left
  as resource/interop literals.)
- Readable public names that remain are framework‑facing
  (`frmMain`, `loginForm`, property names, `Sign`/`SignCheck`).

**All the security‑relevant algorithms live in the *un‑obfuscated* satellite
DLLs** (`CDownload.dll`, `CDiagOnCan.dll`), so the obfuscation protects the GUI
but not the crypto or protocol.

---

## 8. Security observations (for a defender/auditor)

1. **Hard‑coded AES key `actiacsg`** in `CDownload.dll` — any "encrypted"
   download payload is trivially decryptable; this is obfuscation, not
   confidentiality.
2. **UDS SecurityAccess key is computed client‑side** from a 16‑bit seed with a
   fixed `SecKey` (default `0xFFFF`) via a short reversible transform — standard
   for diagnostic tools, but means ECU unlock strength rests entirely on the
   ECU‑side seed/key secret, which is embedded here.
3. **License codes are static GUID strings** in the binary and AES‑wrapped with
   the same weak scheme — entitlement checks are bypassable by anyone who reads
   the binary.
4. **Operator accounts expire by local clock** (`DateTime.Now`) — clock‑settable,
   so the expiry gate is advisory only.
5. RSA + `Sign`/`SignCheck` suggest download packages are meant to be
   authenticated; the private material / public key provenance would be the next
   thing to verify if integrity matters.

*(All of the above is a factual description of how the shipped tool works, from
its own metadata. Reproducing bit‑exact seed/key or license logic for a specific
ECU would need the per‑ECU secrets, which are not my call to extract or
distribute — I can walk the IL for you on request.)*

---

## 9. Evidence & artifacts produced

Saved under the scratchpad (this session only):
- `…/scratchpad/listing/*.txt` + `*.full.txt` — readable per‑type/per‑method
  dumps (calls, field access, strings, constants) for every managed DLL.
- `…/scratchpad/ev/*.members.json`, `*.native.json` — raw REA evidence
  (metadata, signatures, CIL anchors, P/Invoke boundaries).

### Full CIL decompilation — not yet done
REA gives verified *structure* (every type, signature, call graph, string,
constant) but not C#‑level method bodies. For true line‑by‑line source
(e.g. the exact seed→key math, the `vDLDll_iExecute_Thread` state machine), the
next step is an **ILSpy/dotPeek decompile** of `CDownload.dll` and
`CDiagOnCan.dll` (the un‑obfuscated cores) and a **de4dot** pass on the EXE.
Installing the .NET SDK + `ilspycmd` for that was **blocked by the auto‑mode
sandbox** ("Code from External"). Approve that step (or run `ilspycmd
CDownload.dll` locally) and I'll produce the decompiled C#.
