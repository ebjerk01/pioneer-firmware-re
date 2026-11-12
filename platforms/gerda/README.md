# Platform: Panasonic "Gerda"

The SoC under several 2017-era Pioneer AV receivers. Identified from the device tree
(`compatible = "panasonic,gerdac-hwe"`) and driver names in the Linux subsystem.

## Silicon

- **SoC:** Panasonic Semiconductor Solutions *Gerda* automotive SoC.
- **CPU:** dual ARM Cortex-A9 (little-endian), running **AMP** — two operating systems
  side by side, one per core, communicating over an on-chip FIFO/mailbox ("ISC").
- **Peripherals (from the device tree):** Cortex-A9 GIC + TWD timer, `panasonic,l2-system-cache`,
  `panasonic,gerda-timer`, `panasonic,mn-nor` (NOR flash), `panasonic,mn-uart` @ 0x9c01c200,
  `panasonic,mn-sioext` @ 0x9c01c300. Peripheral window around 0x9c000000; GIC/L2 at 0x6000xxxx/0x610cxxxx.
- **Display:** on-chip layer-based display controller (strings `GD_LYR`, `dsp_layer_win`,
  `dsp_layer_scaling`, `LCD_power_on/off`, `WVGA Setting`) driving an 800×480 (WVGA) panel.
- **Video:** Chips&Media **VPU** (`CNM_VPU_DRV`) for decoding phone-projection video.

## Software architecture

```
           ┌─────────────── Gerda SoC (dual Cortex-A9, AMP) ───────────────┐
 LCD  ◄─────┤ Core A — uITRON RTOS  ("BS_ARM" main app)                      │
 amp  ◄─────┤   • HMI / menus (draws via the HW display layers, bitmap UI)   │
 tuner ◄────┤   • audio routing (MC_AUDIO), Bluetooth, iPod/iAP, radio/DSP   │
           │   • ◄── ISC FIFO (iscdrv: isc_send/isc_receive) ──►            │
 USB  ◄─────┤ Core B — Linux (Buildroot/BusyBox)                             │
 Wi-Fi/BT ◄─┤   • smartphone link: CarPlay, Android Auto (libaapsink),       │
           │     AppRadio, iAP2; USB-gadget mux (funcmng); VPU video decode; │
           │     Wi-Fi (Broadcom), wpa_supplicant, GStreamer, ALSA           │
           └───────────────────────────────────────────────────────────────┘
```

Key point for anyone chasing UI performance: **the native menu UI is Core A (uITRON),
not Linux.** The Linux side renders none of the native UI (no framebuffer / DRM / Qt /
GUI libraries exist in its rootfs); its only on-screen role is decoding the *phone's*
projected video that Core A composites as a display layer.

## Linux subsystem (Core B)

- Buildroot 2014.11, BusyBox, glibc 2.19, kernel **3.14.19**.
- Custom `/init` inserts Panasonic drivers then execs BusyBox init:
  `iscdrv` (inter-system comm), `vpu` (video), `hdcpdrv` (HDCP), `gerda_pcm` (audio),
  `panasonic_udc` + `usb_f_iap2` (Apple iAP2 gadget) + `usb_f_ncm` + `g_carplay`/`g_iap2`.
- Connectivity middleware: `libaapsink.so` (Android Auto), `libiap_middleware`/`libiPodiAP1`
  (Apple iAP), `libbt_stack`/`libbt_util` (Bluetooth), AAC/WMA/Vorbis codecs, GStreamer 0.10,
  SQLite, OpenSSL 1.0.0. Broadcom Wi-Fi firmware (`bcm4339_sta.bin`) present.

## Bluetooth / Wi-Fi radio (combo chip)

Wireless is **not** in the Gerda SoC — it's an external **combo chip** providing both radios:

- **Bluetooth** over UART `/dev/ttySM0` (`etc/bluetooth/bt_vendor.conf`,
  `FwPatchFileName = bt_patch.hcd`). The `.hcd` is Broadcom patchram format; the image carries
  `Automotive_BCM89335…hcd`. The product BT (phone/HFP/A2DP) runs here, via a Suntec BT stack
  (`libbt_*.so`, build path `17MainBt/SuntecBt`), with BT UI/control on the uITRON core over ISC.
- **Wi-Fi** over SDIO on the **same combo chip** (`bcm4339_sta.bin` + `bcm4339.txt` nvram).
- The shared image also carries a **Qualcomm** BT path (`hciattach_qca`), so the fitted combo
  part varies by board revision (Broadcom or Qualcomm).

So Wi-Fi and BT are two cores of **one combo chip**, not separate modules. On a **wired** SKU
like the SPH-DA230DAB the Wi-Fi core is unused: there is **no Wi-Fi driver** in the image (no
`bcmdhd.ko`/`cfg80211`), **no AP tooling** (no `hostapd`/`p2p_supplicant`; only client-mode
`wpa_supplicant`), and `/init` has the Wi-Fi/BT insmod/patchram lines commented out. Because the
product Bluetooth runs on the combo chip, the Wi-Fi radio is almost certainly *present but
unused*. See [docs/wireless-carplay-android-auto.md](../../docs/wireless-carplay-android-auto.md).

## `.avh` update image format

A single raw flash image, **no encryption and no signature** observed, laid out as:

```
0x00000000  uITRON "BS_ARM" main app  (HMI + audio/BT/radio; ~31 MB on the images seen)
   ...       Linux kernel  (ARM zImage; compressed piggy, LZO or XZ depending on build)
   ...       flattened device tree (small)
   ...       SquashFS rootfs  (gzip, 128 KB blocks) for the Linux core
   ...       tail
```

`tools/unpack_avh.py` locates these by signature (no fixed offsets) and carves them out.

## Boot / debug

- Kernel bootargs: `console=ttyS0,115200n8 rw init=init root=/dev/mtdblock1
  rootfstype=squashfs noinitrd debug user_debug=31 rootwait`.
- Linux root filesystem is on NOR `mtdblock1`; writable data on `mtdblock2`; `funcmng`
  also touches `mtdblock0`, `mtd6` and an eMMC `mmcblk0p4`.
- **Serial console = root.** `/etc/inittab` runs a getty on `ttyS0`, `ttyS0` is in
  `/etc/securetty`, and `/etc/shadow` gives **root an empty password** — so the Linux
  core's UART yields an unauthenticated root shell. (This is the *connectivity* core; it
  does not by itself speed up or alter the native menus.)
