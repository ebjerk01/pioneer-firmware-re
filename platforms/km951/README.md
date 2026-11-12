# Platform: KM951 (Pioneer wireless generation) — stub

The newer platform behind Pioneer's **wireless**-projection units (e.g. **DMH-ZF9350BT**,
DMH-Z6350BT). Distinct from the wired [Gerda / KM769](../gerda/) generation. Analysis here is
preliminary — the firmware is encrypted, so it has not been unpacked.

## What's known
- Internal code **KM951** (string in the `.avh` header, cf. Gerda = KM769).
- Firmware is still distributed as a single `.avh`, but **much larger** — DMH-ZF9350BT's
  `.avh` is **259,206,048 bytes** (vs 56 MB for Gerda).
- The image is **packed/encrypted**: entropy ≈ **7.98/8.0** across the whole file, with no
  plaintext strings beyond the `DMH-ZF9350BT` / `KM951` header. `tools/unpack_avh.py` finds no
  SquashFS/DTB/zImage by signature (consistent with compression/encryption).
- Scale and structure are consistent with a modern (Qualcomm-class / Android-scale) SoC rather
  than the Gerda Cortex-A9 + uITRON design.
- Capability: wireless Apple CarPlay (wired Android Auto) on the ZF9350BT.

## Open
- Recover the `.avh` container/crypto so the image can be unpacked.
- Identify the exact SoC and OS.
- Confirm whether the SPH-EVO series (wireless CP+AA) is this platform or a late Gerda variant.

## Firmware source
- DMH-ZF9350BT (AU), `DMH-ZF9350BT.avh` inside the zip, from
  `pioneer.com.au/wp-content/uploads/2021/11/DMH-ZF9350BT.zip` (via the Wayback Machine). The
  reachable capture is truncated (~127 MB of the 247 MB zip); enough to confirm KM951 + the
  high-entropy/encrypted nature, not enough to unpack.
