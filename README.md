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
platforms/        per-SoC-platform notes shared by many models
  gerda/          Panasonic "Gerda" (dual Cortex-A9 AMP: uITRON + Linux)
models/           per-model findings
  sph-da230dab/   Pioneer SPH-DA230DAB (and the shared CVJ2392/CVJ4842 image family)
```

## Platforms covered

| Platform | SoC | CPU | OS split | Models (so far) |
|----------|-----|-----|----------|-----------------|
| [gerda](platforms/gerda/) | Panasonic *Gerda* | dual ARM Cortex-A9 (AMP) | uITRON (HMI/audio) + Linux (phone link) | SPH-DA230DAB, MVH-Z5050BT, AVH-Z#### / DMH-Z#### (2017 line) |

## Tools

- [`tools/unpack_avh.py`](tools/unpack_avh.py) — scan a `.avh` image and print/carve its
  regions (main app / kernel / device tree / SquashFS rootfs). No fixed offsets, so it
  generalises across models on the same platform.
- [`tools/fetch_firmware.sh`](tools/fetch_firmware.sh) — re-download the images for a model
  from the archived source URLs and verify their SHA-256.

## Quick start

```sh
# fetch + verify the SPH-DA230DAB images (from the archive; originals are offline)
./tools/fetch_firmware.sh models/sph-da230dab/firmware-sources.md ./fw

# map an image, then carve its parts out
python3 tools/unpack_avh.py ./fw/CVJ2392-K.avh -o ./out
unsquashfs -d ./out/rootfs ./out/rootfs.sqsh
dtc -I dtb -O dts ./out/device-tree.dtb
```
