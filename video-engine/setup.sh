#!/usr/bin/env bash
# Baut die Arbeitsumgebung fuer die Karten-Videos auf. Aufruf: bash setup.sh <arbeitsordner>
set -euo pipefail
W="${1:?Arbeitsordner angeben}"; HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W/build/tex" "$W/audio" "$W/pk" "$W/tilecache"
cd "$W/build" && [ -f package.json ] || npm init -y >/dev/null
npm i three@0.160.0 world-atlas@2.0.2 topojson-client@3.1.0 >/dev/null
# Erd-Texturen: NASA Blue Marble + Relief aus dem Paket basemap-data, Sternenhimmel aus three-globe
cd "$W/pk" && pip download -q --no-deps basemap-data -d bm && unzip -o -q bm/*.whl 'mpl_toolkits/basemap_data/*.jpg'
npm pack three-globe >/dev/null 2>&1 && tar xzf three-globe-*.tgz --wildcards '*/img/night-sky.png'
cp package/example/img/night-sky.png "$W/build/tex/"
python3 -I "$HERE/tools/make_earth_texture.py" "$W/pk/mpl_toolkits/basemap_data" "$W/build/tex"
# Soundeffekte (selbst erzeugt, rechtefrei)
cd "$W/audio"
ffmpeg -v error -y -f lavfi -i "anoisesrc=d=1.4:c=pink:a=0.7" -af "bandpass=f=900:w=1400,afade=t=in:d=0.8:curve=exp,afade=t=out:st=0.8:d=0.6,volume=0.5" swoosh.wav
ffmpeg -v error -y -f lavfi -i "anoisesrc=d=1.1:c=pink:a=0.6" -af "highpass=f=300,lowpass=f=5000,afade=t=in:d=0.6,afade=t=out:st=0.6:d=0.5,volume=0.35" whoosh.wav
ffmpeg -v error -y -f lavfi -i "sine=f=1046:d=0.35" -f lavfi -i "sine=f=1568:d=0.35" -filter_complex "[0][1]amix=2,afade=t=out:st=0.02:d=0.33:curve=exp,volume=0.55" pop.wav
ffmpeg -v error -y -f lavfi -i "sine=f=784:d=0.6" -f lavfi -i "sine=f=1175:d=0.6" -f lavfi -i "sine=f=1568:d=0.6" -filter_complex "[0][1][2]amix=3,afade=t=out:st=0.03:d=0.55:curve=exp,volume=0.7" ding.wav
cp "$HERE"/scenes/*.html "$HERE"/scenes/*.json "$W/build/"
echo "Fertig: $W"
