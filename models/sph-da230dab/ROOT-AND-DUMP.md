# SPH-DA230DAB — getting a root shell, dumping & flashing

How to get in, back up, and modify this unit. The enabling fact throughout: **the `.avh`
update is unsigned and has no integrity check** (see [FINDINGS](FINDINGS.md)), and the
hackable Linux core owns the flash and the USB port.

> Everything here is for a unit **you own**. A failed flash can brick it. Dump the stock
> firmware first and keep the stock `.avh` to recover.

## Entry-vector matrix

| Vector | What it gets you | Effort | Risk | Notes |
|--------|------------------|--------|------|-------|
| **UART serial console** | root shell (empty root pw) | low (needs opening unit + USB-TTL) | low | `ttyS0` 115200 8N1; getty + `securetty`. The clean entry. |
| **Modified-rootfs update** (below) | solder-free root + full flash dump | medium | medium (flash write) | Unsigned update → flash a rootfs that self-dumps. No soldering. |
| **USB A-to-A to a PC** (the Android trick) | nothing | — | — | Not Android, no ADB, host-mode default. Doesn't work here. |
| **Crafted USB stick (parser exploit)** | code exec if a vuln exists | high | low | Auto-mounts FAT/NTFS as root; unsigned update parser. Vuln-hunting. |
| **CarPlay NCM IP tunnel** | network into Linux core | high | low | Needs MFi handshake; not plug-and-play. |
| **JTAG** | hardware debug / brick recovery | high | low | Separate pads by the SoC (not the USB port); may be fused off. |

## Confirmed: the updater does NOT block a modified image

- `.avh` has **no signature** and **no stored checksum** (header is model-code + `GERDAVER:NN.NN`
  then `0xFF` padding; tail is zero).
- `/usr/bin/rom_update` is a trivial 4 KB ELF that just writes a buffer to `/dev/mtdblock0`.
- funcmng does the erase/write/verify: its "verify" strings sit next to
  `failed to flash write offset 0x%08x rw_size 0x%08x` + the `MEMERASE` ioctl — a **post-write
  read-back** (confirms the flash took *your* bytes), **not** a hash check against a stored
  reference. So a modified image passes. (Caveat: confirmed structurally + by string context,
  not yet by full decompilation of the verify function.)

## The self-dumping-rootfs technique (solder-free dump + root)

The device already ships the tools: **`/usr/sbin/mtd_debug`** (read/write flash),
**`/usr/sbin/flashcp`**, and a minimal BusyBox. So we inject a boot script into the rootfs and
flash the modified `.avh`; on boot it dumps every flash partition to a USB stick.

Build (see [`tools/build_selfdump_rootfs.sh`](../../tools/build_selfdump_rootfs.sh)):
1. Carve + unpack the stock rootfs (`unpack_avh.py` → `unsquashfs`).
2. Add `etc/init.d/S99zdump` (template in `tools/`) — a background watcher that, whenever a USB
   stick mounts (`/media/N`), runs `mtd_debug read /dev/mtdN … → USB` for every line in
   `/proc/mtd`, plus `cpuinfo`/`meminfo`/`uname`.
3. Drop dead weight to make room — the glib codegen `*.pyc`/`*.pyo` are build artifacts (no
   Python interpreter on the device) and free ~300 KB.
4. `mksquashfs … -comp gzip -b 131072 -all-root` — must stay **≤ the original rootfs size**
   (the region is `[0x225F400, 0x354B400)`; right after it is a **calibration table** — don't
   overrun it).
5. Splice the new squashfs into the stock `.avh` at `0x225F400`, zero-pad to the region length,
   leave the app/kernel/DTB **and the trailer byte-identical**. Total size unchanged.
6. Version: the stock base is `08.24`; it flashes onto any unit on ≤ 8.23 as a normal upgrade.
   If the unit is already on 8.24, bump the tag with [`tools/set_version.py`](../../tools/set_version.py).

**Improvement (from prior art, below):** the stock BusyBox has **no telnetd**, so UART is the
only shell by default. Bundle a **static BusyBox (or dropbear)** with telnetd into the modified
rootfs and start it from the script to also get a **network root shell** (e.g. telnet:23, no
password) over the CarPlay/NCM USB-ethernet or Wi-Fi — the technique the CarPlay-adapter RE
(below) used.

**Recovery:** keep the stock `.avh`; re-flash it. Ideally have UART attached as a fallback
before the first write.

## Prior art (other people's work)

- **LennartF22/pioneer-firmware** (GitHub) — tools to build modified SD-card images for Pioneer
  **AVH/AVIC** head units from an update package, *including adding a root shell to the system
  partition*. Those are **SD-card-boot** units (different from this NOR-flash Gerda unit) and use
  a "Warp!!" fast-boot **snapshot** — note their warning that `CATCH_SNAPSHOT` can hard-brick.
  Closest public work; validates the `.avh`→unpack→add-root→repack approach.
- **rgerganov/gen5fw** — Hyundai/Kia/Genesis Gen5 nav: patches the rootfs from the official
  update package and flashes via USB. Same technique, different vendor.
- **sec1.dk — Wireless CarPlay adapter RE** — got a root shell by **bringing their own BusyBox**
  (base lacked telnetd) → telnet:23, no password. Source of the bundle-telnetd idea above.
- **YT9216B / Carlink (XDA)** — Android head-unit rooting; "backup first (readback)" and
  "custom firmware gives telnet access, flash it before other mods".
- **cybergibbons — "Copying firmware from embedded devices"** — `mtd` → USB dumping; notes that
  the bootloader/U-Boot region may be invisible from the OS, which is why a **raw mtd dump** of
  every partition matters (captures the uITRON bootloader + clock-init we can't see otherwise).

**Scene gap:** there's **no public firmware-level root/dump project for the Gerda SPH-DA2xx
generation.** Public SPH-DA work is phone-side mirroring (AppRadio Unchained). This RE appears to
be ahead of the public state for this exact platform.
