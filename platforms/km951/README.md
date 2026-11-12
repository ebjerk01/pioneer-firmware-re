# Platform: KM9xx (Pioneer wireless generation) — stub

The newer platform family behind Pioneer's **wireless**-projection units. Distinct from the
wired [Gerda / KM769](../gerda/) generation and **encrypted**, so not yet unpacked.

Confirmed members (all big, high-entropy `.avh`, header `<MODEL>&KM9xx/X...`):

| Model | Internal code | `.avh` size | Wireless | Header tag |
|-------|---------------|-------------|----------|-----------|
| DMH-ZF9350BT | **KM951** | 259 MB | wireless CarPlay (wired AA) | `&KM951/XNGS` |
| SPH-EVO64DAB | **KM975** | 284 MB (v3.09) | wireless CP **and** AA | `&KM975/XNEW` |

**Key result for the Gerda units:** every wireless Pioneer checked so far (KM951, KM975) is this
newer **encrypted** platform — **none are Gerda**. So there is **no Gerda-based wireless sibling**
to lift a matching `bcmdhd.ko` from for the wired KM7xx units. The SPH-EVO line, despite the
styling lineage with the SPH-DA units, moved to **KM975** — so it cannot unlock WiFi on a
Gerda/KM769 unit like the SPH-DA230DAB.

## What's known
- Internal code **KM951** / **KM975** (string in the `.avh` header, cf. Gerda = KM769).
- Firmware is still a single `.avh`, but **much larger** (259–284 MB vs 56 MB for Gerda).
- The image is **packed/encrypted**: entropy ≈ **7.94–7.98/8.0** across the whole file, with no
  plaintext beyond the `<MODEL>` / `KM9xx` header. `tools/unpack_avh.py` finds no SquashFS/DTB/
  zImage by signature (consistent with encryption).
- Scale/structure consistent with a modern (Qualcomm-class / Android-scale) SoC, not the Gerda
  Cortex-A9 + uITRON design.

## Open
- Recover the `.avh` container/crypto so these images can be unpacked.
- Identify the exact SoC and OS.

## Firmware sources (local, not committed — encrypted vendor images)
- DMH-ZF9350BT (AU): `pioneer.com.au/wp-content/uploads/2021/11/DMH-ZF9350BT.zip` (Wayback;
  reachable capture truncated ~127 MB of 247 MB — enough to confirm KM951 + entropy).
- SPH-EVO64DAB v3.09: `SPH-EVO64DAB.avh` (284 MB) inside `SPH-EVO64DAB_FW_Ver309.ZIP`
  (md5 `d6fa9d72…`). Confirmed KM975 + entropy on the owner's machine; not transferred.
