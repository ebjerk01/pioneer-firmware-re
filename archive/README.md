# Pioneer firmware archive (catalog)

A preservation snapshot of Pioneer's live firmware bucket `pioneer03.s3.amazonaws.com/firmware/`
(captured 2026-11-12), in case the bucket is withdrawn. **This repo holds only the catalog**
(filenames, sizes, SHA-256) — not the proprietary `.zip`/`.avh` binaries, which stay in private
storage.

- [`pioneer03-firmware-manifest.txt`](pioneer03-firmware-manifest.txt) — 37 firmwares, ~9.3 GB.

## How to re-fetch
The bucket denies `ListBucket` but allows `GetObject`, so any file can be pulled directly if you
know its exact key:

```
curl -O "https://pioneer03.s3.amazonaws.com/firmware/<FILENAME>"
```

Verify against the SHA-256 in the manifest. Filenames are **case-sensitive**; naming conventions
seen: `<MODEL>_FW_Ver<NNN>.ZIP`, `<MODEL>_FW_Ver_<NNN>.zip`, `<MODEL>_<SIG>_<REGION>_FW_VER<NNN>.ZIP`
(AVIC nav), and `<MODEL>_A<NNNN>.zip` (basic radios). Exact filenames come from each model's
Pioneer support page (the bucket is not listable).

## What's inside
- **Plaintext (Gerda / KM769):** SPH-DA230DAB, SPH-DA130DAB, SPH-DA120, AVH-X8600/8800BT, etc. —
  unpackable (see [platforms/gerda](../platforms/gerda/)).
- **Encrypted "20MD"/"23MD" (KM8xx/KM9xx):** SPH-EVO64DAB (×5), SPH-EVO93DAB (×6),
  SPH-EVO950DAB (×6), DMH-Z6350BT, AVIC nav units — see
  [platforms/km951](../platforms/km951/) for the container format + why the body isn't yet
  decryptable.
