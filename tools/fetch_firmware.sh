#!/usr/bin/env bash
# fetch_firmware.sh — download a model's firmware images from their (archived)
# source URLs and verify SHA-256. Reads a model's firmware-sources.md.
#
# The markdown table rows are expected to contain, somewhere in the row:
#   `<sha256>` ... (<url>)
# i.e. a 64-hex code span and a parenthesised URL. Lines without both are skipped.
#
# Usage: ./tools/fetch_firmware.sh models/<model>/firmware-sources.md [OUTDIR]
set -euo pipefail

SRC="${1:?usage: fetch_firmware.sh firmware-sources.md [outdir]}"
OUT="${2:-./fw}"
mkdir -p "$OUT"

# Pull (sha256, url) pairs out of the markdown.
grep -oE '`[0-9a-f]{64}`[^(]*\(https?://[^)]+\)' "$SRC" | while read -r line; do
    sha=$(printf '%s' "$line" | grep -oE '[0-9a-f]{64}' | head -1)
    url=$(printf '%s' "$line" | grep -oE 'https?://[^)]+' | head -1)
    name=$(basename "${url%%\?*}")
    dst="$OUT/$name"
    echo ">> $name"
    if [ -f "$dst" ] && [ "$(sha256sum "$dst" | cut -d' ' -f1)" = "$sha" ]; then
        echo "   already present and verified"
        continue
    fi
    curl -fL --retry 3 -o "$dst" "$url"
    got=$(sha256sum "$dst" | cut -d' ' -f1)
    if [ "$got" != "$sha" ]; then
        echo "   !! SHA-256 MISMATCH: expected $sha got $got" >&2
    else
        echo "   verified $sha"
    fi
done
echo "done -> $OUT"
