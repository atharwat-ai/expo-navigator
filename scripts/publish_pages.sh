#!/usr/bin/env bash
# Build dist/index.html and publish it to the gh-pages branch (GitHub Pages),
# the address every QR code opens: https://atharwat-ai.github.io/expo-navigator/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
python3 scripts/build_offline.py   # dist/kiosk-offline.html, for kiosks with no internet
{ printf '<!DOCTYPE html>\n<html lang="en">\n<head>\n'; cat expo-navigator.html; printf '\n</html>\n'; } > dist/index.html
W="$(mktemp -d)"
git fetch -q origin gh-pages
git worktree add -q --detach "$W" origin/gh-pages
cp dist/index.html "$W/index.html"; cp dist/kiosk-offline.html "$W/kiosk-offline.html"; touch "$W/.nojekyll"
( cd "$W" && git add index.html kiosk-offline.html .nojekyll && { git diff --cached --quiet && echo "gh-pages already up to date"; } || { git commit -qm "Publish the navigator map ($(git -C "$OLDPWD" rev-parse --short HEAD))" && git push -q origin HEAD:gh-pages && echo "published to gh-pages"; } )
git worktree remove --force "$W"
