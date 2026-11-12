# Wireless CarPlay / Android Auto — feasibility across Pioneer models

Question this answers: the SPH-DA230DAB ships a Wi-Fi firmware blob, so could it do
**wireless** CarPlay / Android Auto? Short answer: **not through firmware on the Gerda
platform** — wireless is a *different, newer hardware generation*. Below is the evidence,
including a cross-model firmware comparison.

## 1. What wireless CarPlay / Android Auto actually requires

| Need | Why | Present on SPH-DA230DAB? |
|------|-----|--------------------------|
| A Wi-Fi radio | the session runs over Wi-Fi | combo chip likely **present** (see §3) |
| A Wi-Fi **driver** (`bcmdhd.ko`/`cfg80211`) | to drive the radio | **No** — only an inert firmware blob |
| **AP / P2P** bring-up (`hostapd` / `p2p_supplicant`) + DHCP | the head unit hosts the Wi-Fi link | **No** — only client-mode `wpa_supplicant` |
| Bluetooth LE / handshake | phone & HU exchange Wi-Fi creds over BT first | BT present, but the **wireless-handoff** half is absent |
| Wireless-projection code in the CarPlay/AA stack | advertise + move the session to Wi-Fi | **No** — libs have only the wired path + Bonjour/BT-pairing |

So on the DA230DAB every software piece needed for wireless is missing or disabled, even
though the radio hardware is probably sitting there (its Bluetooth runs on the same combo
chip — see the platform's [Bluetooth/Wi-Fi architecture](../platforms/gerda/README.md)).

## 2. Cross-model firmware comparison

| Unit | Internal code | SoC / OS | Wireless CP/AA | Firmware | Image |
|------|---------------|----------|----------------|----------|-------|
| **SPH-DA230DAB** (this project) | **KM769** | Panasonic **Gerda**, dual Cortex-A9, uITRON + Linux 3.14 | none (wired only) | 56 MB `.avh`, **plaintext, unsigned** | analysed |
| MVH-2300NEX / MVH-Z5050BT | KM769 | same Gerda image | none | same image | wired siblings |
| **DMH-ZF9350BT** | **KM951** | newer platform (Qualcomm-class / Android-scale) | **wireless CarPlay** (wired AA) | **247 MB** `.avh`, **packed/encrypted** (entropy ≈ 7.98/8) | downloaded, see below |
| SPH-EVO93DAB | (unconfirmed) | (unconfirmed) | wireless CP **and** AA | firmware not obtainable here | styling successor; platform not confirmed |

**The finding:** Pioneer's wireless units are a **different, newer platform generation**
(KM9xx) with a much larger, **encrypted** firmware, whereas the Gerda wired generation
(KM7xx) ships a small plaintext image. There is **no close Gerda-based wireless sibling** to
port a wireless stack from. Wireless is a hardware/platform leap, not a Gerda config.

### DMH-ZF9350BT evidence (the reference wireless unit)
- Firmware: `DMH-ZF9350BT.avh`, **259,206,048 bytes** (the Gerda `.avh` is 56 MB).
- Header strings: `DMH-ZF9350BT`, `KM951` (platform code; cf. DA230 = KM769).
- Entropy ≈ **7.98/8.0 across the whole image** → compressed/encrypted; **no plaintext
  strings** (the Gerda image is ~7.4 and full of readable paths/symbols). So even reading it
  needs the unpack/decrypt step first — a different problem class from the Gerda image.
- (A Wayback capture of this image is itself truncated; a full copy is 247 MB.)

## 3. Is the Wi-Fi radio physically present on the DA230DAB?

Probably **yes**. Its Bluetooth is configured on a Broadcom combo chip over UART `ttySM0`
(`bt_vendor.conf`, `bt_patch.hcd`), and the Wi-Fi core of that **same combo chip** uses
`bcm4339_sta.bin` over SDIO. Since the Bluetooth works, the combo part is fitted — so the
Wi-Fi radio is there, just unused (no driver, no AP stack). Only opening the unit and checking
the board near the antennas would make this certain.

## 4. Practical conclusion

- **Firmware mod on the DA230:** conceivable (radio likely present, image is unsigned) but
  would require porting a Wi-Fi driver for kernel 3.14.19 + `hostapd`/P2P + DHCP + a
  wireless-projection stack that **does not exist on this platform** — you'd be writing it, not
  copying it. Very high effort, high brick risk, unsupported. Not worth it.
- **The real answer:** a **USB wireless CarPlay/Android Auto adapter** (CarlinKit, AAWireless,
  Ottocast, ~$40–70) plugs into the USB port, presents itself as a *wired* phone to the head
  unit, and bridges to your phone over its own Wi-Fi/BT. Wireless projection on this exact unit,
  no firmware risk.

## Open / unconfirmed
- SPH-EVO93DAB (wireless CP+AA, the direct styling successor) — firmware could not be obtained
  from the archives reachable here, so whether it is a later Gerda variant or a new platform is
  **unconfirmed**. If obtained, it would close the "is there ever a Gerda-wireless build" question.
