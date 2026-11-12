# Platform: Freescale/NXP i.MX6 + Android (Pioneer AVIC navigation)

A third Pioneer platform, distinct from [Gerda](../gerda/) (Panasonic/uITRON) and the
[encrypted 20MD generation](../km951/). The **AVIC** navigation units run **Android on a
Freescale/NXP i.MX6** — plaintext and openable like any Android head unit.

## Identity (from AVIC-Zx30BT, product `PJ200BOT`)
- **SoC:** Freescale/NXP **i.MX6Q/D/S** (ARM Cortex-A9), board **"Jupiter"**, reference
  `MX6Q SABER_LITE`, `imx6_volans`. `ro.board.platform=imx6`.
- **OS:** **Android 4.2.2 (SDK 17, Jelly Bean)** — frozen old Android; the Ver106 build is dated
  2024-04-26 yet still 4.2.2. Pioneer-branded (`ro.product.manufacturer/brand=Pioneer`).
- **Boot:** standard Android — kernel cmdline `console=ttymxc0,115200 init=/init
  video=mxcfb0:dev=ldb,bpp=32 … androidboot.hardware=freescale`.

## Container format "a55a5aa5" (Pioneer flash image)
```
0x000  magic A5 5A 5A A5, size/checksum fields, product code (e.g. "PJ200BOT")
0x200  Android boot image  (ANDROID! magic; kernel + gzip-cpio ramdisk)
 ...   Android sparse (0x3aff26ed) ext4 partitions (system, etc.), squashfs, recovery images
```
Plaintext throughout (entropy ~3.8 for the nav units with maps; ~0.07 for the older/sparse ones).
Images are large: AVIC-Zx ≈ 1.5 GB uncompressed. Unsparse with `simg2img`, then mount ext4.

## Security posture
- `default.prop`: `ro.secure=1`, `ro.debuggable=0`, `persist.sys.usb.config=mtp` — production.
- **But `/system/xbin/su` and `/system/bin/su` are present** — a notable root lead worth
  investigating (no SuperSU/Magisk app, so likely a bare/dev `su`). ADB-secure props present.
- Old Android 4.2.2 = a large known-CVE surface. These are classic rootable Android head units.

## Members (in the archive)
- Rich (full Android + maps, ~1.5 GB): **AVIC-Zx10BT / Zx20BT / Zx30BT** (DAB + DAB-C, EU5).
- Older/sparse (512 MB, mostly padding): **AVIC-Fx7x / Fx8x**, **SPH-DA120** (AppRadio 4),
  **AVH-X8600BT / AVH-X8800BT**.

## Next
- `simg2img` the system partition → `build.prop`, app list, the `su` binary's real behaviour.
- Parse the `a55a5aa5` partition table fully (offsets/sizes/names).
- Compare to the common Chinese i.MX6 Android head units (likely shared BSP).
