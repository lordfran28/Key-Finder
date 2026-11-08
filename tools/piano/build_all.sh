#!/bin/bash
# Build every song in charts.SONGS (the beginner arrangement, with sound) into out/.
cd "$(dirname "$0")"
for s in $(python3 -c "import charts; print(' '.join(charts.SONGS))"); do
  python3 build.py $s 2>&1 | tail -1
done
