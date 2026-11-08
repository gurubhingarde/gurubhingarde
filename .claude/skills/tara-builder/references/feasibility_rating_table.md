# Attack Feasibility Rating — Very Low / Low / Medium / High

## Overview

Feasibility measures how difficult it is for a threat agent to execute a specific attack scenario. Rate based on five factors, and assign the **worst (lowest) factor rating as the overall feasibility**.

**Principle**: If ANY factor is "Very Low", the attack is "Very Low" feasibility. If the worst factor is "Low", feasibility is "Low", etc.

---

## Five Feasibility Factors

### 1. Elapsed Time Required

Time the attacker needs to develop exploit, prepare, and execute.

| Rating | Timeline | Descriptor | Examples |
|--------|----------|-----------|----------|
| **Very Low** | Year or more | Long-term research, publication, tool development | Full reverse-engineering of closed-source firmware; development of novel 0-day exploit; multi-year academic research |
| **Low** | Months (3–12) | Significant engineering, possibly assisted by published work | Analyzing published firmware; reverse-engineering known algorithm; developing custom CAN tools; obtaining and analyzing similar vehicle |
| **Medium** | Weeks (2–4) | Moderate engineering, using existing tools and documentation | Writing exploit using existing framework; modifying public PoC; standard protocol analysis |
| **High** | Days (1–7) or less | Minimal development, tools available "off-the-shelf" | Running publicly available scanner; using manufacturer test tools; executing published exploit scripts |

**Rationale**: 
- Nation-state attackers have years; casual hackers have days. 
- Novel attacks require research; known attacks are plug-and-play.
- Closed-source, obfuscated systems take longer than open or well-documented ones.

---

### 2. Specialist Expertise Required

The level of cybersecurity and domain knowledge needed.

| Rating | Descriptor | Examples |
|--------|-----------|----------|
| **Very Low** | Multiple experts needed | Requires cross-functional team (cryptography expert + firmware reverse-engineer + embedded systems engineer + security researcher); consensus knowledge spanning multiple domains |
| **Low** | Expert-level expertise | PhD-level cybersecurity researcher; lead automotive OEM security engineer; high-end red team; published exploit author |
| **Medium** | Proficient expertise | Self-taught hacker with 5+ years CAN/automotive protocol experience; security researcher familiar with automotive domain; senior embedded developer with security training |
| **High** | Layman expertise | Script kiddie with basic Python/C; technician with OEM tools; enthusiast following online tutorials; automotive mechanic with computer access |

**Rationale**:
- Default assumption: "layman" is most permissive for threat model.
- Self-taught or informal training counts as "proficient".
- Formal education alone doesn't overcome domain gap.

---

### 3. Knowledge of Item (Proprietary / Public)

Information available to attacker about the system, firmware, design.

| Rating | Descriptor | Sources | Difficulty |
|--------|-----------|---------|-----------|
| **Very Low** | Critical (completely closed) | Reverse-engineering only; no documentation | Full static/dynamic analysis; decryption; deobfuscation required |
| **Low** | Sensitive (restricted distribution) | Internal docs leaked; OEM service manuals; academic papers on similar systems | Significant but guided analysis; understanding accelerated by partial knowledge |
| **Medium** | Restricted (some public info) | Published standards (CAN, UDS); security advisories; partial open-source; OEM public APIs | Combined reverse-engineering + public specs; standard protocol analysis |
| **High** | Public (open or well-known) | Open-source firmware; public repositories; published firmware images; protocol analyzers available | Direct analysis; no reverse-engineering needed; well-documented attack vectors |

**Rationale**:
- Closed systems (firmware encryption, obfuscation) require research.
- Open-source or publicly available firmware is exploitable immediately.
- Published standards (CAN, UDS) are layman-readable.
- Leaked OEM docs accelerate attack development significantly.

---

### 4. Window of Opportunity

How often and for how long is the attack window available?

| Rating | Descriptor | Vehicle State | Attack Availability |
|--------|-----------|----------------|--------------------| 
| **Very Low** | Difficult | Specific driving condition, encryption active, real-time detection | <0.1% of operating time; once per year; during brief state transition |
| **Low** | Moderate | Specific mode, user action, limited connectivity | 1–10% of operating time; during scheduled maintenance; via physical access window |
| **Medium** | Easy | Common condition, low vigilance required | 10–50% of operating time; during normal operation; via adjacent network |
| **High** | Unlimited | Always available, always vulnerable, no special condition | >50% of operating time; network-accessible always; persistent attack surface |

**Rationale**:
- Attack surface available *during normal use* is high opportunity.
- OTA or service connections are limited (low).
- Attacks requiring vehicle to be in specific mode or location are difficult.
- Persistent network access (cellular, WiFi) is unlimited.

**Examples**:
- **Very Low**: Firmware modification window only during ECU flash (technician-initiated, logged)
- **Low**: Debug interface accessible during service but not in field
- **Medium**: CAN bus always transmitting, but attacker must be physically adjacent
- **High**: OTA update channel available 24/7 to any connected vehicle

---

### 5. Equipment Required

Tools, hardware, test gear, knowledge resources needed.

| Rating | Equipment Type | Cost | Availability | Examples |
|--------|---|------|---|---------|
| **Very Low** | Multiple bespoke tools | $100K+ | Proprietary, custom-built, one-of-a-kind | Hardened security lab; proprietary RF equipment; custom silicon; formal verification tools |
| **Low** | Bespoke specialized | $10K–$100K | Custom-built or rare commercial | Protocol analyzer ($10K); CAN-HV isolator (custom); reverse-engineering lab setup; IDA Pro + plugins ($5K) |
| **Medium** | Specialized commercial | $500–$10K | Niche market, not trivial but available | ELM327 CAN reader ($50–$500); oscilloscope ($2K); automotive diagnostic software ($1K); JTAG/SWD debuggers ($500–$5K) |
| **High** | Standard/free tools | <$500 | Commodity, off-the-shelf, open-source | Wireshark, Burp Suite, WireShark, custom Python scripts, automotive OEM diagnostic tools (leaked or public), Linux tools |

**Rationale**:
- Exotic hardware (specialized RF, custom chips) is very low feasibility.
- Commercial oscilloscopes and logic analyzers are medium (cost + learning curve).
- Leaked OEM tools or widely available open-source = high.
- Software-only attacks using public frameworks = high.

**Examples**:
- **Very Low**: Requires formal verification environment (Frama-C, TLA+) + proprietary security lab
- **Low**: JTAG debugger + IDA Pro + custom Python CAN toolkit (typical red-team budget)
- **Medium**: PiCAN2 + standard desktop tools + online tutorials
- **High**: Python + open-source CAN library + leak of firmware image from web

---

## Feasibility Lookup Summary

| Rating | Elapsed Time | Expertise | Knowledge | Opportunity | Equipment | Real-World Example |
|--------|---|---|---|---|---|---|
| **Very Low** | Year+ | Multiple experts | Critical (closed) | Difficult | Multiple bespoke | Full reverse-engineering of encrypted, obfuscated proprietary firmware by dedicated research team |
| **Low** | Months | Expert | Sensitive (leaked docs) | Moderate | Bespoke | Academic security research on known protocols with specialized lab; professional red-team with time budget |
| **Medium** | Weeks | Proficient | Restricted (partial public) | Easy | Specialized | Experienced hacker using combination of public specs + reverse-engineering; moderate investment in tools |
| **High** | Days | Layman | Public (open) | Unlimited | Standard | Script kiddie running public exploit tools; using leaked OEM firmware or open-source code |

---

## Computing Overall Feasibility

**Rule**: The overall feasibility rating = the worst (most favorable to attacker) of the five factors.

**Example 1**: Firmware integrity attack
- Elapsed Time: Weeks (Medium) — develop custom verification bypass
- Expertise: Proficient (Medium) — standard exploitation techniques
- Knowledge: Public (High) — firmware available on GitHub
- Opportunity: High — always present
- Equipment: Standard (High) — any laptop

**Overall**: High (all factors Medium or High)

---

**Example 2**: Authentication key extraction from secure enclave
- Elapsed Time: Years (Very Low) — requires novel attacks on security chip
- Expertise: Expert (Low) — specialized cryptanalysis
- Knowledge: Critical (Very Low) — proprietary hardware design
- Opportunity: Moderate (Low) — requires physical access + specialized setup
- Equipment: Multiple bespoke (Very Low) — custom lab equipment

**Overall**: Very Low (multiple factors Very Low/Low)

---

## STRIDE-Specific Guidance

### Spoofing
- **High feasibility** if no message authentication (layman + public protocols)
- **Low feasibility** if cryptographic message signing (requires breaking crypto)

### Tampering
- **High feasibility** if unprotected writable memory
- **Medium feasibility** if requires privilege escalation
- **Low feasibility** if integrity checks or secure boot enforced

### Repudiation
- **High feasibility** if no logging or logs are writable
- **Low feasibility** if cryptographic audit trail with separate recorder

### Information Disclosure
- **High feasibility** if data unencrypted and accessible
- **Medium feasibility** if encrypted at rest but decryption possible
- **Low feasibility** if encrypted and keys protected in hardware security module

### Denial of Service
- **High feasibility** if no rate limiting or input validation
- **Medium feasibility** if watchdog or recovery mechanisms exist
- **Low feasibility** if multiple redundant defenses and isolation

### Elevation of Privilege
- **High feasibility** if default credentials, hardcoded passwords
- **Medium feasibility** if weak access control logic
- **Low feasibility** if formal verification, privilege separation, secure boot
