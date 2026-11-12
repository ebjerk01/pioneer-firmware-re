# pioneer-firmware-re

Reverse-engineering notes and tooling for **Pioneer car head-unit firmware**.

The goal is to understand how these units work internally — the SoC, the operating
system(s), the boot and update flow, the HMI, and what is (and isn't) realistically
modifiable — starting from the firmware images Pioneer ships as `.avh` update files.
It is organised so that additional models can be added over time.

> **No proprietary firmware is redistributed here.** This repo contains original
> analysis, hashes and tooling only. Firmware images must be obtained from Pioneer
> or a public archive; see each model's `firmware-sources.md`. Analysis is for
> interoperability, repair and research on hardware one owns.

## Layout

```
tools/            reusable analysis tooling (image unpacker, fetch+verify helper)
docs/             cross-model topics (e.g. wireless CarPlay / Android Auto feasibility)
platforms/        per-SoC-platform notes shared by many models
  gerda/          Panasonic "Gerda" (dual Cortex-A9 AMP: uITRON + Linux)
  km951/          newer wireless-projection platform (encrypted .avh) — stub
models/           per-model findings
  sph-da230dab/   Pioneer SPH-DA230DAB (and the shared CVJ2392/CVJ4842 image family)
```

## Platforms covered

| Platform | Internal code | SoC / OS | Firmware | Models (so far) |
|----------|---------------|----------|----------------|-----------------|
| [gerda](platforms/gerda/) | KM697–KM793+ | Panasonic *Gerda*, dual Cortex-A9, uITRON + Linux | **plaintext, openable** | SPH-DA230DAB, SPH-DA130DAB, AVH-A3100/A3200DAB, AVH-Z7100DAB, MVH-Z5050BT … |
| [imx6-android](platforms/imx6-android/) | PJ200 ("Jupiter") | Freescale/NXP **i.MX6** (Cortex-A9), **Android 4.2.2** | **plaintext, openable** (`a55a5aa5`) | AVIC-Zx10/20/30BT, AVIC-Fx7x/Fx8x, SPH-DA120, AVH-X8600/8800BT |
| [km951](platforms/km951/) (20MD/23MD) | KM830/837/951/975 | newer encrypted generation | **encrypted** (`20MD`/`23MD`) | SPH-EVO64/93/950DAB, DMH-Z6350/ZF9350BT |

## Topics

- [docs/wireless-carplay-android-auto.md](docs/wireless-carplay-android-auto.md) — can a wired
  unit be made to do wireless CarPlay/Android Auto? Cross-model comparison + the honest answer.

## Tools

- [`tools/unpack_avh.py`](tools/unpack_avh.py) — scan a `.avh` image and print/carve its
  regions (main app / kernel / device tree / SquashFS rootfs). No fixed offsets, so it
  generalises across models on the same platform.
- [`tools/fetch_firmware.sh`](tools/fetch_firmware.sh) — re-download the images for a model
  from the archived source URLs and verify their SHA-256.
- [`tools/set_version.py`](tools/set_version.py) — show or rewrite the ASCII version tag(s) in
  a `.avh` (the images are unsigned and carry no stored checksum). **Flashing a mislabelled
  image can brick a unit — read the warning in the file.**

## Quick start

```sh
# fetch + verify the SPH-DA230DAB images (from the archive; originals are offline)
./tools/fetch_firmware.sh models/sph-da230dab/firmware-sources.md ./fw

# map an image, then carve its parts out
python3 tools/unpack_avh.py ./fw/CVJ2392-K.avh -o ./out
unsquashfs -d ./out/rootfs ./out/rootfs.sqsh
dtc -I dtb -O dts ./out/device-tree.dtb
```
