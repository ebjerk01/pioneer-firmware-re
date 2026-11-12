#!/usr/bin/env python3
"""
set_version.py — rewrite the version tag(s) in a Pioneer "Gerda"-platform .avh image.

On this platform the firmware version is stored as plain ASCII in two places, and the
on-device updater gates a flash on model-code + version (it carries no signature and no
stored checksum of the image — see platforms/gerda/README.md). This tool lets you set the
version an image *reports*, e.g. to make an older build pass the unit's downgrade block.

    python3 set_version.py IN.avh --to 08.25 -o OUT.avh
    python3 set_version.py IN.avh --show        # just print current version/model

It patches, in place of the original and nowhere else:
  * the metadata tag   "GERDAVER:XX.YY"  (the partition version marker)
  * the in-app copy    "0123456789ABCDEF" + "XX.YY"

Both replacements are the same byte length, so nothing shifts and no checksum needs redoing.

!!  DANGER  !!  This produces an image that LIES about its version. Flashing a mislabelled or
    older image can brick a unit. Only ever do this on hardware you own, after you have a full
    flash dump to recover from, and ideally after confirming the on-device updater does no
    extra validation. This tool only edits bytes; it does not and cannot make flashing safe.
"""
import argparse, re, sys

GERDAVER = re.compile(rb'GERDAVER:(\d\d\.\d\d)')
INAPP    = re.compile(rb'0123456789ABCDEF(\d\d\.\d\d)')
FILECODE = re.compile(rb'(CVJ\d{4}-[A-Z])')

def show(buf):
    g = GERDAVER.search(buf)
    fc = FILECODE.search(buf, max(0, (g.start()-48) if g else 0)) if g else None
    print(f"  GERDAVER tag : {g.group(1).decode() if g else '(none)'}"
          f"  @ 0x{g.start()+9:x}" if g else "  GERDAVER tag : (none)")
    i = INAPP.search(buf)
    if i:
        print(f"  in-app ver   : {i.group(1).decode()}  @ 0x{i.start()+16:x}")
    if g:
        j = buf.rfind(b"CVJ", g.start()-48, g.start())
        if j >= 0:
            print(f"  file code    : {buf[j:j+12].split(bytes([0]))[0].decode()}  @ 0x{j:x}")

def main():
    ap = argparse.ArgumentParser(description="show/patch the version tag in a Gerda .avh")
    ap.add_argument("image")
    ap.add_argument("--to", help="new version, format NN.NN (e.g. 08.25)")
    ap.add_argument("-o", "--out", help="output file (required with --to)")
    ap.add_argument("--show", action="store_true", help="just print current version")
    args = ap.parse_args()

    buf = bytearray(open(args.image, "rb").read())
    print(f"image: {args.image}")
    show(buf)
    if args.show or not args.to:
        return
    if not re.fullmatch(r"\d\d\.\d\d", args.to):
        sys.exit("--to must be NN.NN, e.g. 08.25")
    if not args.out:
        sys.exit("need -o OUT.avh with --to")
    new = args.to.encode()

    n1 = n2 = 0
    def repl_g(m):
        nonlocal n1; n1 += 1; return b"GERDAVER:" + new
    def repl_i(m):
        nonlocal n2; n2 += 1; return b"0123456789ABCDEF" + new
    buf = GERDAVER.sub(repl_g, bytes(buf))
    buf = INAPP.sub(repl_i, buf)

    if len(buf) != len(open(args.image, "rb").read()):
        sys.exit("internal error: size changed")  # must never happen (equal-length edits)
    with open(args.out, "wb") as f:
        f.write(buf)
    print(f"\npatched -> {args.out}  (GERDAVER x{n1}, in-app x{n2}, version set to {args.to})")
    print("\nverify:")
    show(bytearray(buf))

if __name__ == "__main__":
    main()
