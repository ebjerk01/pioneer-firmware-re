# SPH-DA230DAB — modification feasibility

What can realistically be changed, ranked by payoff vs effort/risk. The `.avh` is unsigned, so
firmware mods are *possible*; the hard part is locating the right bytes in the closed uITRON app
and flashing safely (see [ROOT-AND-DUMP](ROOT-AND-DUMP.md)).

| Mod | Feasible? | Effort / risk | Notes |
|-----|-----------|---------------|-------|
| **Full flash dump + root** | **Yes** | low–med | UART (clean) or the self-dumping-rootfs update. Do this first — everything else needs it. |
| **Snappier UI (cut animations)** | likely | med | Best payoff. UI is **animation-gated**: fixed `200ms next step` timers + an easing module (`NS_EasingAnimation.c`). Shortening the cosmetic ones ≈ "animations off → instant". Must locate the timing constants (needs a Ghidra pass — debug strings aren't directly xref'd) and keep hardware-settle delays (e.g. widemode) intact. |
| **Wireless CarPlay/Android Auto** | no (firmware) | — | Different/newer platform (KM951, encrypted). Wi-Fi driver/AP stack/wireless-projection code all absent here. Use a USB dongle. See [docs/wireless…](../../docs/wireless-carplay-android-auto.md). |
| **More than 5 paired BT devices** | hard / not worth it | high | **Not a single constant.** The paired list is a fixed-size array (`f_paired_list_info.main_item_info[N]` in `ui_ws_bt_devicelist.c`) + a fixed 5-row UI screen + the Suntec stack's bonding store (`A2dpConfigureMaxRemoteDevices`). Bumping only the limit check overflows the array. Raising it safely means resizing structures in a closed binary and reworking the UI layout — disproportionate for marginal gain. Practical answer: delete an old pairing / factory reset. |
| **Overclock** | conceivable, don't | high / **brick** | Undocumented clock controller; a bad value hangs pre-boot (unrecoverable without JTAG). Coupled to DDR/display clocks. Low payoff. See [FINDINGS](FINDINGS.md). |
| **Remove "apps" to speed up** | n/a | — | No removable apps — monolithic uITRON + one Linux daemon. Idle sources cost ~0 CPU. |
| **Downgrade / version relabel** | yes | low build / med flash | `set_version.py`; unsigned image, 2-byte edit. See [FINDINGS](FINDINGS.md). |

## Why the UI is slow (summary)
Entry-level Panasonic **Gerda-C** (dual Cortex-A9, ~2016), bitmap/HW-layer UI with timed easing
animations, assets from slow NOR. It's hardware- and animation-bound, not bloat. The two real
levers are **(1) cut the animation timers** (firmware) and **(2) live in CarPlay/Android Auto**
(offloads the UI to the phone — biggest real-world win, zero risk).
