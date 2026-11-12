# Pioneer SPH-DA230DAB — full specification

Two parts: **A) published specs** (Pioneer / manual / retailers) and **B) researched
internals** (recovered from the firmware images in this repo). Items marked *(verify)* were
not fully confirmed against an official Pioneer spec sheet.

---

## A. Published specifications

| | |
|---|---|
| Type | 2-DIN **mechless** multimedia AV receiver (no disc drive) |
| Region / market | Europe (internal region code **EU5**) |
| Display | **7" WVGA**, 800 × 480, "clear-type" **capacitive** touchscreen, 16:9 |
| Max power output | **50 W × 4** (MOSFET) |
| Continuous (RMS) | ~22 W × 4 typical for this Pioneer class *(verify)* |
| Pre-outs | 2 × RCA pre-out *(verify count)* |
| Tuner | FM / MW (AM) + **DAB / DAB+ / DMB** digital radio (RDS) |
| Bluetooth | **v4.1**, pairs up to 2 devices; profiles A2DP, HFP, SPP (handsfree + audio streaming) |
| Apple CarPlay | Yes, **wired** (USB) |
| Android Auto | Yes, **wired** (USB) |
| AppRadio Mode | Yes |
| iPod / iPhone | Yes, via USB (iAP) |
| Music apps | Built-in control for Spotify and Pandora |
| USB | 1 × USB (rear) |
| Camera input | Rear-view camera input (camera sold separately) |
| EQ / tuning | 13-band graphic EQ, time alignment, crossover (HPF/LPF) *(verify bands)* |
| Chassis | Double-DIN (approx. 178 × 100 mm face) |

Not supported: wireless CarPlay/Android Auto; no built-in navigation (uses phone projection);
no disc, no HDMI in.

---

## B. Researched internals (from firmware RE)

### Platform & silicon
| | |
|---|---|
| Internal model / project code | **KM769** (firmware family `CVJ2392` / `CVJ4842`) |
| Sibling models (same platform) | **MVH-2300NEX** (US), **MVH-Z5050BT** (AU); related KM770: SPH-DA130DAB, MVH-1400NEX, SPH-DA138TV; KM775: AVH-ZL5150BT |
| SoC | **Panasonic "Gerda"** automotive SoC (`panasonic,gerdac-hwe`) |
| CPU | **Dual ARM Cortex-A9** (little-endian), running **AMP** (two OSes, one per core) |
| RAM | DDR (exact size not yet determined from firmware) |
| Main flash | **NOR** (`panasonic,mn-nor`); ≥64 MB (update image is 54 MB). Partitions: `mtdblock0`, `mtdblock1` (Linux rootfs), `mtdblock2` (data), `mtd6` |
| Extra storage | eMMC present (`mmcblk0p4` referenced) |
| Display controller | On-SoC hardware **layer compositor** (`GD_LYR`, `dsp_layer_scaling`) → WVGA 800×480 |
| Video decoder | **Chips&Media VPU** (`CNM_VPU_DRV`) — decodes phone-projection video |
| Audio | `gerda_pcm` / ALSA; decoders for AAC, WMA, Vorbis; iAP/CarPlay audio streaming |
| Wireless radio (firmware present) | Broadcom **BCM4339** Wi-Fi + **BCM89335** Bluetooth blobs are in the image (used by wireless-capable siblings; this model's CarPlay/AA are wired) |

### Operating systems
| Core | OS | Role |
|------|----|------|
| Core A | **uITRON RTOS** ("BS_ARM" app) | HMI / menus, LCD + display layers, audio routing, Bluetooth, iPod/iAP, tuner/DAB, DSP |
| Core B | **Linux 3.14.19** (Buildroot 2014.11, BusyBox 1.22.1, glibc 2.19) | Smartphone link: CarPlay, Android Auto (`libaapsink`), AppRadio, iAP2; USB-gadget mux; VPU video; Wi-Fi/BT |
| Inter-core link | On-chip FIFO/mailbox **ISC** (`iscdrv`: `isc_send`/`isc_receive`) | |

### Tuner / region capability (platform-wide; this unit = DAB/EU)
- DAB / DAB+ (this model), plus platform support for **HD Radio** and **SiriusXM** on the US
  NEX variants. Tuner middleware: `com.indexcom.Tuner2.1`.

### Software build / versioning
| | |
|---|---|
| Firmware version tag | `GERDAVER:08.24` (ASCII, in a metadata header) + file code `CVJ2392-K` |
| Latest firmware | 8.24 / 18.24 / 28.01 (Feb 2020); downgrade blocked by the unit |
| Userland libs | OpenSSL 1.0.1j, SQLite, GStreamer 0.10 |

### Debug / security (Linux core)
| | |
|---|---|
| Serial console | `ttyS0` @ 115200 8N1, kernel `debug user_debug=31`, rootfs mounted `rw` |
| Root login | **Empty root password** + getty on `ttyS0` in `securetty` → UART = root shell |
| Update image | **Unsigned**; no stored checksum/signature — gated only by model code + version string |

---

*Published specs: Pioneer manual and retailer listings. Internals: recovered from the
`CVJ2392`/`CVJ4842` firmware images — see [FINDINGS.md](FINDINGS.md) and
[firmware-sources.md](firmware-sources.md).*
