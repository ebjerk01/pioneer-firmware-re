# Platform: newer encrypted generation — the "20MD"/"23MD" container (KM8xx/KM9xx)

Pioneer's generation *after* the plaintext [Gerda / KM769](../gerda/) units. The firmware is an
encrypted container; the only plaintext is a 256-byte header. Analysed from the EVO64DAB version
set (v304–309) in the preserved [archive](../../archive/pioneer03-firmware-manifest.txt).

## The "20MD" / "23MD" container header (reverse-engineered, plaintext)

```
off  size  field
0x00  4    magic: ASCII "20MD" (or "23MD" — a later format revision, e.g. SPH-EVO950DAB)
0x04  4    header size = 0x00000100 (256 bytes)
0x08  4    0
0x0C  4    payload/image size (LE) — tracks the file size
0x10  4    0
0x14  32   model name, ASCII, null-padded (e.g. "SPH-EVO64DAB")
0x34  ..   "&KM<code>/<tag>" platform string (e.g. "&KM975/XNEW")
0x40  ..   "XNEW"/"XNGS" tag again, then [b0][b1][ver][03 01 01] — byte @0x46 = fw minor
           version (v304→04, 305→05, 306→06, 307→07, 309→09); then 0xFF flash-erase padding
0x100 ..   ENCRYPTED body
```

## Platform-code map (from the header `&KM###` field)

| Model | Container | Platform code | Tag |
|-------|-----------|---------------|-----|
| SPH-DA230DAB (and all Gerda units) | *(none — plaintext)* | **KM769** | — |
| SPH-EVO93DAB | 20MD | **KM830** | XNEW |
| DMH-Z6350BT | 20MD | **KM837** | XNGS |
| DMH-ZF9350BT | 20MD | **KM951** | XNGS |
| SPH-EVO64DAB | 20MD | **KM975** | XNEW |
| SPH-EVO950DAB | **23MD** | (TBD) | — |

Note: EVO64DAB (KM975) and EVO93DAB (KM830) are **different platforms** — same firmware *size*
per version but different bytes (different SoC/build). Do not assume cross-model identity.

## Encryption analysis — body is robustly encrypted (NOT offline-crackable)

From five adjacent EVO64DAB versions (v304–309):

- Body (0x100→EOF) entropy is uniformly **~7.98–8.0/8** — no plaintext islands, no compression
  magics, no segment table (single `20MD` magic at 0x0).
- **No ECB**: 16-byte block duplication is **0.00%** (only 0xFF/0x00 padding repeats).
- **100% version-diff**: *no* 64 KB block is identical between any two versions (even adjacent
  304↔305), and the first body bytes at 0x100 differ across all versions.

→ The body is encrypted with a per-image key/IV (stream/CTR or CBC), likely over already-
compressed data. The classic weaknesses are all absent, so **version-diff cryptanalysis is
defeated** and the image cannot be decrypted from the firmware alone. The key lives in the
device (SoC secure-boot / TrustZone), not in the `.avh`. Decryption would need a key extracted
from a unit, an updater vulnerability, or a leak.

## Why preserve it anyway
These encrypted images are archived (see the manifest) so that **if** a KM8xx/KM9xx key ever
surfaces — from rooting a unit, a leak, or future RE — the whole generation can be decrypted and
studied retroactively. The container header is already reversed; only the body cipher/key remain.

## Open
- Extract a device key (needs root on an actual KM8xx/KM9xx unit — its own entry problem).
- Diff the "20MD" vs "23MD" header revisions for format changes.
- Identify the SoC/OS once a body can be decrypted.
