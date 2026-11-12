# Pioneer SPH-DA230DAB — findings

2-DIN 6.8" WVGA AV receiver (DAB+, Bluetooth, Apple CarPlay, Android Auto, AppRadio).
Built on the Panasonic **Gerda** platform — see [`platforms/gerda`](../../platforms/gerda/)
for the shared SoC / OS / `.avh`-format detail. This file covers what is specific to this
model and the shared `CVJ2392`/`CVJ4842` image family.

## Summary

- Runs a dual-OS AMP design on one Gerda SoC: a **uITRON** core draws the native HMI and
  handles audio/BT/radio, and a **Linux** core handles the smartphone link (CarPlay/Android
  Auto/AppRadio). They talk over an on-chip FIFO (ISC).
- Update images are a single raw `.avh` flash image (56,409,088 bytes) with **no encryption
  and no signature** — see [`firmware-sources.md`](firmware-sources.md) for files + hashes.
- **The native menu UI is the uITRON core, not Linux** — relevant to anyone chasing the
  sluggish UI (see "Performance" below).

## Firmware family & variant diff

- Latest firmware **8.24 / 18.24 / 28.01** (Feb 2020); no newer exists; downgrade blocked.
- 8.24 = `CVJ2392-K.avh`, 18.24 = `CVJ4842-B.avh`.
- A 64 KB block-diff of 8.24 vs 18.24: **only the first ~13 MB differs** (the uITRON
  main-app partition). Kernel + device tree + SquashFS rootfs are **byte-identical**.
  So "8.xx" vs "18.xx" is a main-app (market/trim) variant over one shared Linux image.
- The same images are shared across the 2017 Pioneer AV line (the AU **MVH-Z5050BT** ships
  the identical `CVJ2392-*` + `CVJ4842-B`).

## Image layout (CVJ2392-K, 8.24)

```
0x00000000  uITRON "BS_ARM" main app   (HMI/menus, LCD + display layers, audio, BT, iAP, radio)
0x01F02C00  Linux kernel  (ARM zImage, LZO piggy)
0x0225EA00  flattened device tree (gerda, 2520 bytes)
0x0225F400  SquashFS 4.0 rootfs (gzip, 128 KB blocks, ~19 MB, 1072 inodes) — the Linux core
0x0354B07F  trailer (~500 KB)
0x035CBC00  EOF
```
Reproduce with `python3 tools/unpack_avh.py CVJ2392-K.avh -o out`.

## Linux rootfs highlights

- Buildroot 2014.11 / BusyBox / glibc 2.19, kernel 3.14.19, built 2019-11-10.
- Connectivity middleware: `libaapsink.so` (Android Auto), Apple iAP (`libiap_middleware`,
  `libiPodiAP1`), Bluetooth stack (`libbt_stack`/`libbt_util`), GStreamer 0.10, ALSA,
  SQLite, OpenSSL 1.0.0; Broadcom BCM4339 Wi-Fi firmware + wpa_supplicant.
- `/opt/revision/revision.txt`: Spotify apl r87, iAP apl r522, Pandora apl r207.

## Security posture (Linux core)

- `/etc/shadow`: **`root::...`** → empty root password.
- `/etc/inittab`: getty on `ttyS0`; `/etc/securetty` includes `ttyS0`; kernel `debug
  user_debug=31 rw`.
- → the Linux core's **UART is an unauthenticated root shell** (115200 8N1). This is the
  *connectivity* core; it does not render or control the native menus.

## Performance (the slow native UI)

The laggy menus are rendered by the **uITRON core** (closed ARM binary, the first ~31 MB of
the image) on a ~2015 Cortex-A9, drawing a bitmap/HW-layer UI from NOR flash. So:

- The image is unsigned and therefore modifiable in principle, **but** speeding up the native
  menus means patching that closed uITRON binary — very high effort, high brick risk, and the
  bottleneck is largely hardware/asset-bound, so expected gain is low. Poor ROI.
- The Linux side (which we can read freely) renders none of the native UI — it only affects
  phone-projection smoothness (CarPlay/Android Auto/AppRadio), not the Pioneer menus.

## Update mechanism, signing & versioning

- **Updates are unsigned.** The `.avh` has no appended signature (tail is zero-padded, no
  PKCS#7/ASN.1/RSA), and the image stores **no checksum of itself** that the device could
  verify against. The only hash Pioneer ships is an MD5 inside the zip, checked by a Windows
  `.bat` on the PC before copying to USB — it never reaches the unit. (The `RSA`/`PKCS`/
  `verify` strings in the image are in the CarPlay/iAP auth libraries, not the updater.)
- **What the unit checks is model + version**, stored as plain ASCII in a 44-byte metadata
  header between the app and the kernel:
  ```
  0x01F01910  "CVJ2392-K"       file/model code (null-padded 16 bytes)
  0x01F01920  "GERDAVER:08.24"  version tag (then 0xFF flash-erase padding — no CRC field)
  ```
  A second ASCII copy of the version sits in the app's build-info table right after the
  string `0123456789ABCDEF` (at 0x0059B1B0 in this image). Confirmed across versions:
  `CVJ2392-J`/`08.23`, `CVJ4842-B`/`18.24`, `CVJ2392-H`/`08.21`.
- Internally the platform is **KM769**; the model table lists sibling identities
  SPH-DA230DAB / MVH-2300NEX / MVH-Z5050BT (KM769) and SPH-DA130DAB / MVH-1400NEX /
  SPH-DA138TV (KM770), AVH-ZL5150BT (KM775).
- **Downgrade / relabel feasibility:** because there is no signature and no stored checksum,
  the reported version is just two editable ASCII fields. `tools/set_version.py` rewrites both
  (equal-length, so nothing shifts). A test bump of the 8.21 image to `08.25` changed exactly
  **2 bytes** and the image stayed valid — i.e. nothing in the image integrity-checks those
  bytes. In principle this lets an older build pass the unit's downgrade block.
  **Caveat:** this is confirmed only at the image-structure level; the on-device updater's
  exact flash-time behaviour has not yet been disassembled, and flashing a mislabelled image
  to a single unit with no recovery path risks a brick. Do not flash blind — get a UART root
  shell + full flash dump first.

## uITRON app load address (recovered)

The main-app ARM reset vector table is at image offset **0x1A00**, and the app loads such
that **vaddr = file_offset + 0x200FE600** (so the vector table sits at a clean
**0x20100000**). Verified: pointers resolve to real string starts (e.g. the pointer at
0x5A9B60 → `SPH-DA130DAB`, 0x5A9BA4 → `Pioneer / AV Receiver`). Use this base to load the
main-app region (file 0x1A00 onward) into a disassembler.

## Open threads

1. Disassemble the on-device updater (now possible with base 0x200FE600) to confirm exactly
   how it compares versions and that it does no extra flash-time validation.
2. Map the uITRON HMI: display-layer compositor (`GD_LYR`, `dsp_layer_*`), the menu asset
   format, and the task structure.
3. Map the ISC inter-core protocol (`isc_send`/`isc_receive` message formats).
4. Map the full NOR/eMMC partition table (`mtdblock0..2`, `mtd6`, `mmcblk0p4`).
