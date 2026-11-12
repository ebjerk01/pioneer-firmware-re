#!/usr/bin/env python3
"""
unpack_avh.py — map and carve a Pioneer ".avh" head-unit firmware image.

Pioneer distributes updates for many AV receivers as a single raw flash image
named like CVJ####-X.avh (wrapped in a zip with a whole-file MD5). The images seen
so far on the Panasonic "Gerda" platform (SPH-DA230DAB, MVH-Z5050BT, AVH-Z####,
DMH-Z####, ...) are a plain concatenation of regions, no encryption and no header:

    [ uITRON "BS_ARM" main app ][ Linux zImage ][ DTB ][ SquashFS rootfs ][ tail ]

This tool scans an .avh for the recognisable regions (SquashFS, flattened device
tree, ARM zImage + its compressed payload) and optionally carves them out. It makes
no assumption about fixed offsets, so it should work across models on this platform.

Usage:
    python3 unpack_avh.py IMAGE.avh                 # just print the layout
    python3 unpack_avh.py IMAGE.avh -o OUTDIR       # also carve regions to OUTDIR

Carved files (when -o given): rootfs.sqsh, device-tree.dtb, zImage.bin
Unpack the rootfs with: unsquashfs -d rootfs rootfs.sqsh
Decode the dtb with:     dtc -I dtb -O dts device-tree.dtb
"""
import argparse, struct, sys, os

def find_all(buf, needle, limit=64):
    out, off = [], 0
    while len(out) < limit:
        i = buf.find(needle, off)
        if i < 0:
            break
        out.append(i)
        off = i + 1
    return out

def parse_squashfs(buf, off):
    # SquashFS 4.0 little-endian superblock
    (magic, inodes, mkts, blksz, frags, comp, blog, flags,
     ids, vmaj, vmin) = struct.unpack_from("<IIIIIHHHHHH", buf, off)
    bytes_used = struct.unpack_from("<Q", buf, off + 40)[0]
    comp_names = {1: "gzip", 2: "lzma", 3: "lzo", 4: "xz", 5: "lz4", 6: "zstd"}
    if vmaj != 4 or blksz == 0 or bytes_used == 0 or off + bytes_used > len(buf):
        return None
    return dict(off=off, end=off + bytes_used, size=bytes_used, inodes=inodes,
                comp=comp_names.get(comp, comp), block=blksz, ver=f"{vmaj}.{vmin}")

def parse_dtb(buf, off):
    magic, total = struct.unpack_from(">II", buf, off)
    if total < 0x100 or total > 0x200000 or off + total > len(buf):
        return None  # reject implausible sizes (filters false positives)
    ver = struct.unpack_from(">I", buf, off + 20)[0]
    if ver > 0x20:
        return None
    return dict(off=off, end=off + total, size=total)

def parse_zimage(buf, off):
    # ARM zImage: magic 0x016f2818 at off+0x24; start/end at off+0x28
    start, end = struct.unpack_from("<II", buf, off + 0x28)
    size = end - start
    if size <= 0 or size > len(buf):
        return None
    info = dict(off=off, size=size)
    window = buf[off:off + size]
    for name, mag in (("xz", b"\xfd7zXZ"), ("gzip", b"\x1f\x8b\x08"),
                      ("lzo/lzop", b"\x89LZO"), ("lzma", b"\x5d\x00\x00")):
        j = window.find(mag)
        if j >= 0:
            info["payload"] = name
            info["payload_off"] = off + j
            break
    return info

def main():
    ap = argparse.ArgumentParser(description="Map/carve a Pioneer .avh firmware image")
    ap.add_argument("image")
    ap.add_argument("-o", "--out", help="carve regions into this directory")
    args = ap.parse_args()

    with open(args.image, "rb") as f:
        buf = f.read()
    print(f"image: {args.image}  size: {len(buf)} (0x{len(buf):x})")

    regions = []

    for off in find_all(buf, b"hsqs"):
        sq = parse_squashfs(buf, off)
        if sq:
            regions.append(("SquashFS", sq))
            print(f"  SquashFS 4.0  @ 0x{sq['off']:08x} .. 0x{sq['end']:08x}  "
                  f"{sq['size']} bytes  {sq['comp']}  block={sq['block']}  inodes={sq['inodes']}")

    for off in find_all(buf, b"\xd0\x0d\xfe\xed"):
        dt = parse_dtb(buf, off)
        if dt:
            regions.append(("DTB", dt))
            print(f"  Device tree   @ 0x{dt['off']:08x} .. 0x{dt['end']:08x}  {dt['size']} bytes")

    for off in find_all(buf, struct.pack("<I", 0x016f2818)):
        z = off - 0x24
        if z < 0:
            continue
        zi = parse_zimage(buf, z)
        if zi:
            regions.append(("zImage", zi))
            extra = ""
            if "payload" in zi:
                extra = f"  payload={zi['payload']} @ 0x{zi['payload_off']:08x}"
            print(f"  ARM zImage    @ 0x{zi['off']:08x}  ~{zi['size']} bytes{extra}")

    # Everything before the first kernel/dtb/squashfs is the main (uITRON) app region.
    firsts = [r[1]["off"] for r in regions if r[0] in ("zImage", "DTB", "SquashFS")]
    if firsts:
        app_end = min(firsts)
        print(f"  Main app      @ 0x00000000 .. 0x{app_end:08x}  "
              f"(uITRON 'BS_ARM' region, ~{app_end // (1024*1024)} MB)")

    if not args.out:
        return
    os.makedirs(args.out, exist_ok=True)
    def carve(name, a, b):
        p = os.path.join(args.out, name)
        with open(p, "wb") as g:
            g.write(buf[a:b])
        print(f"  wrote {p} ({b-a} bytes)")
    for kind, r in regions:
        if kind == "SquashFS":
            carve("rootfs.sqsh", r["off"], r["end"])
        elif kind == "DTB":
            carve("device-tree.dtb", r["off"], r["end"])
        elif kind == "zImage":
            carve("zImage.bin", r["off"], r["off"] + r["size"])

if __name__ == "__main__":
    sys.exit(main())
