# SPH-DA230DAB — firmware sources & hashes

Pioneer's own download links are offline (their `pioneer01` S3 bucket now 404s, and
`pioneer.com.au` upload paths return 403). The images below were recovered from the
**Internet Archive Wayback Machine**. `tools/fetch_firmware.sh` reads this file, downloads
each image and verifies its SHA-256.

The distribution is a `.zip` containing the real `.avh` flash image (plus, in the base
package, a `Readme.txt`, a whole-file `.md5`, and a renamed `md5sum.exe`). The latest
firmware is **8.24 / 18.24 / 28.01 (Feb 2020)**; downgrade is blocked by the unit.

## Update file selection (per Pioneer's instructions)

| Current version on unit | Update file | Target version |
|-------------------------|-------------|----------------|
| lower than 8.24 | `CVJ2392-K.avh` | 8.24 |
| 18.00 – 18.24 | `CVJ4842-B.avh` | 18.24 |
| 28.01 | (already current) | 28.01 |

The same `CVJ2392`/`CVJ4842` images are shared across the 2017 Pioneer AV line
(e.g. the Australian **MVH-Z5050BT** ships the identical `CVJ2392-I/J/K` + `CVJ4842-B`).

## Zip packages (SHA-256 of the `.zip`, and the archived URL)

| Zip | SHA-256 | Source (Wayback) |
|-----|---------|------------------|
| SPH-DA230DAB 8.24 (`CVJ2392-K.avh`) | `b9cc499ef4230a318db73d16031ee1a81741dd32a64fe260bec48bb97a3e6b15` | (https://web.archive.org/web/20200416033825id_/https://www.pioneer.com.au/wp-content/uploads/2017/09/CVJ2392-K.avh_.zip) |
| SPH-DA230DAB 18.24 (`CVJ4842-B.avh`) | `af5f2c9d1752494e42eb63c072320e1827d9d2631d747dbeeffae13de3013d1f` | (https://web.archive.org/web/20200416033946id_/https://www.pioneer.com.au/wp-content/uploads/2017/09/CVJ4842-B.avh_.zip) |
| CVJ2392 base (8.09) | `2d9ace44ab0f0851c6ba875ebc253c8226be20785910b768f78f721a83e93d5b` | (https://web.archive.org/web/20200416033301id_/https://www.pioneer.com.au/wp-content/uploads/2017/09/CVJ2392.zip) |
| CVJ2392-F | `a8996b83735c3dfb2a6eca1b8001bbcf76b4524e2373343156b3f7619bd1b9d9` | (https://web.archive.org/web/20180408155617id_/https://www.pioneer.com.au/wp-content/uploads/2017/09/CVJ2392-F.zip) |
| CVJ2392-J (8.23) | `560b6153260049e4f550a230b3c35a150eb6dd267cfe6ad03bcac593713bcbb7` | (https://web.archive.org/web/20200416033629id_/https://www.pioneer.com.au/wp-content/uploads/2017/09/CVJ2392-J.zip) |
| MVH-Z5050BT (`CVJ2392-I.avh`) | `c57e85f0f5a9481e80c309e8b8b37a3cc026b2210ad3493a4aec88141457e0f2` | (https://web.archive.org/web/20200416033451id_/https://www.pioneer.com.au/wp-content/uploads/2017/09/MVH-Z5050BT.zip) |

## `.avh` payloads (SHA-256 of the image inside the zip)

All payloads are exactly **56,409,088 bytes**.

| File | SHA-256 |
|------|---------|
| `CVJ2392-K.avh` (8.24) | `7880f51cd89f08a136ca65ec0ec1b885fe30e289384b82f7ea336e74003dc5ca` |
| `CVJ4842-B.avh` (18.24) | `c0fb50923efa1155bad414cfe083ccb82ca9cc29df637f414542a9ce669bb47f` |
| `CVJ2392.avh` (base/8.09) | `567489250acefa5ed8170bc4083423e4886009bdd446d61898103919f10711c7` |
| `CVJ2392-F.avh` | `da4d435addf4b93cfccbaafcfa1b4f24af447d0682d2dc0c0611eede14185add` |
| `CVJ2392-J.avh` (8.23) | `9937f9d2f53835c3acd1592f50dcf4a9c165429fc6bff89099568ffbb9a3655d` |

## Notes

- 8.24 (`-K`) vs 18.24 (`-B`): a 64 KB block-diff shows **only the first ~13 MB differs**
  (the uITRON main-app partition); the kernel, device tree and SquashFS rootfs are
  byte-identical. "8.xx" vs "18.xx" is a main-application (market/trim) variant over one
  shared Linux image.
- Change history: 8.24 (Feb 2020) only fixed "no sound from rear speakers after a call"
  vs 8.23 (Jun 2019).
