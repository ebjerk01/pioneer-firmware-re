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

## Open threads

1. Recover the uITRON app's load/base address (ARM reset vector table is at image offset
   0x1A00; absolute data pointers cluster in 0x2000_0000 — base recovery still in progress)
   so the main app can be loaded into a disassembler with correct addresses.
2. Map the uITRON HMI: display-layer compositor (`GD_LYR`, `dsp_layer_*`), the menu asset
   format, and the task structure.
3. Map the ISC inter-core protocol (`isc_send`/`isc_receive` message formats).
4. Map the full NOR/eMMC partition table (`mtdblock0..2`, `mtd6`, `mmcblk0p4`) and check
   whether the on-device updater validates anything before accepting a custom `.avh`.
