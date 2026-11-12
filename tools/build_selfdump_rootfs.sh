#!/usr/bin/env bash
# build_selfdump_rootfs.sh — turn a stock Pioneer Gerda .avh into a "self-dumping" image:
# a modified rootfs that, on boot, dumps every flash partition to a USB stick (mtd_debug)
# and leaves root available on the UART. Solder-free full-flash backup for a unit you own.
#
# Usage: build_selfdump_rootfs.sh STOCK.avh OUT.avh [tools/S99zdump]
#
# !! UNSIGNED-UPDATE abuse on hardware you own. A failed flash can brick the unit. Keep the
# !! stock .avh to recover, and ideally attach UART first. Verify the partition map (/proc/mtd)
# !! and the updater's behaviour on your unit before trusting this.
set -euo pipefail
STOCK="${1:?stock .avh}"; OUT="${2:?out .avh}"; SCRIPT="${3:-$(dirname "$0")/S99zdump}"
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT

python3 "$(dirname "$0")/unpack_avh.py" "$STOCK" -o "$work" >/dev/null
[ -f "$work/rootfs.sqsh" ] || { echo "no squashfs found in $STOCK"; exit 1; }

# locate the squashfs region inside the .avh (start offset + byte length)
read SQ_OFF SQ_LEN < <(python3 - "$STOCK" <<'PY'
import sys,struct
d=open(sys.argv[1],"rb").read(); i=d.find(b"hsqs")
print(i, struct.unpack_from("<Q",d,i+40)[0])
PY
)
REGION_END=$(( SQ_OFF + SQ_LEN ))           # stock squashfs end; pad region runs to next data

unsquashfs -d "$work/root" -n "$work/rootfs.sqsh" >/dev/null
install -m0755 "$SCRIPT" "$work/root/etc/init.d/S99zdump"
# reclaim space: glib codegen python bytecode is dead weight (no interpreter on device)
rm -f "$work/root"/usr/share/glib-2.0/codegen/*.pyc "$work/root"/usr/share/glib-2.0/codegen/*.pyo 2>/dev/null || true

mksquashfs "$work/root" "$work/new.sqsh" -comp gzip -b 131072 -all-root -noappend -no-progress >/dev/null
NEW=$(stat -c%s "$work/new.sqsh")
echo "stock squashfs: $SQ_LEN  modified: $NEW"
[ "$NEW" -le "$SQ_LEN" ] || { echo "ERROR: modified rootfs ($NEW) > stock region ($SQ_LEN); drop more files"; exit 1; }

python3 - "$STOCK" "$work/new.sqsh" "$OUT" "$SQ_OFF" "$SQ_LEN" <<'PY'
import sys
stock=bytearray(open(sys.argv[1],"rb").read()); mod=open(sys.argv[2],"rb").read()
off=int(sys.argv[4]); ln=int(sys.argv[5])
stock[off:off+ln]= mod + b"\x00"*(ln-len(mod))          # replace region, keep total size + trailer
open(sys.argv[3],"wb").write(stock)
print("wrote", sys.argv[3], len(stock), "bytes (app/kernel/dtb/trailer untouched)")
PY
echo "NOTE: base image version is unchanged; bump with set_version.py if the unit rejects it as a downgrade."
