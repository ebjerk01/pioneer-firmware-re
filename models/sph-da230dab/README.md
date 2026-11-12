# SPH-DA230DAB

Pioneer 2-DIN 7" WVGA (800×480) AV receiver (DAB+, Bluetooth, CarPlay, Android Auto,
AppRadio), on the Panasonic [Gerda](../../platforms/gerda/) platform. Internal code **KM769**.

- [SPECS.md](SPECS.md) — full specification (published + researched internals)
- [FINDINGS.md](FINDINGS.md) — analysis specific to this model + the CVJ2392/CVJ4842 family
- [ROOT-AND-DUMP.md](ROOT-AND-DUMP.md) — how to get root, dump the flash, and flash safely (entry-vector matrix, self-dumping-rootfs technique, prior art)
- [MODS.md](MODS.md) — modification feasibility (UI speed, Bluetooth limit, overclock, wireless, …)
- [firmware-sources.md](firmware-sources.md) — image URLs + SHA-256 (fetch with `tools/fetch_firmware.sh`)

Platform-level detail (SoC, dual-OS AMP architecture, `.avh` format, boot/debug) lives in
[platforms/gerda](../../platforms/gerda/).
