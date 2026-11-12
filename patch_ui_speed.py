#!/usr/bin/env python3
"""
patch_ui_speed.py — speed up the SPH-DA230DAB native UI source/video transitions.

The uITRON HMI paces its source-change / widemode / video-path ("video_in wait time")
transitions with fixed step timers. On firmware CVJ2392-K (8.24) these are three
`mov r0, #200` (200 ms) constants in the transition state machine. Lowering them makes
source switching (incl. to/from CarPlay/AppRadio) noticeably snappier.

    python3 patch_ui_speed.py CVJ2392-K.avh --ms 50 -o OUT.avh

Offsets (verified for CVJ2392-K.avh; the tool checks the bytes before writing):
    0x21FB84, 0x21FC04, 0x21FC74  = 200 ms  -> set to --ms
  (0x220BE8 = 40 ms, 0x220C04/0x220C20 = 20 ms are left alone by default)

!! These are partly HARDWARE-SETTLE delays (the video decoder / display layer reconfigure).
!! 50-100 ms is a safe, noticeable speedup; <=20 ms is aggressive and may briefly glitch the
!! video path on a source switch. UNTESTED on hardware — flash only with a recovery path
!! (keep the stock .avh; ideally UART + a flash dump first). See models/sph-da230dab/MODS.md.
"""
import argparse, struct, sys
SITES = [0x21FB84, 0x21FC04, 0x21FC74]   # the three 200ms transition-step timers
STOCK = bytes.fromhex("c800a0e3")        # ARM: mov r0, #0xc8 (200)

def enc_mov_r0(ms):
    if not (0 <= ms <= 255):
        sys.exit("--ms must be 0..255 (single-byte ARM immediate)")
    return bytes([ms, 0x00, 0xA0, 0xE3])  # mov r0, #ms

def main():
    ap = argparse.ArgumentParser(description="speed up DA230 native UI transitions")
    ap.add_argument("image"); ap.add_argument("--ms", type=int, default=50)
    ap.add_argument("-o", "--out")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    b = bytearray(open(a.image, "rb").read())
    ok = all(b[o:o+4] == STOCK for o in SITES)
    print(f"image: {a.image}  stock 200ms timers present at all sites: {ok}")
    for o in SITES:
        print(f"  {o:#08x}: {b[o:o+4].hex()}")
    if a.show: return
    if not ok:
        sys.exit("bytes don't match CVJ2392-K; wrong firmware/version — aborting")
    if not a.out: sys.exit("need -o OUT.avh")
    new = enc_mov_r0(a.ms)
    for o in SITES: b[o:o+4] = new
    open(a.out, "wb").write(b)
    print(f"\npatched 3 transition timers 200ms -> {a.ms}ms (mov r0,#{a.ms} = {new.hex()}) -> {a.out}")
    print("flash via the unsigned-update path; keep the stock .avh to recover.")

if __name__ == "__main__":
    main()
