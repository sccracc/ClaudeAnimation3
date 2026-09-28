#!/bin/bash
# Render the whole film in parallel chunks, then concat and mux with the soundtrack.
set -e
cd "$(dirname "$0")/.."
NF=$(python3 -c "import sys;sys.path.insert(0,'.');from anim.render import total_frames;print(total_frames())")
J=${JOBS:-4}
mkdir -p build/chunks
rm -f build/chunks/*.mp4 build/chunks/list.txt
PIDS=()
for i in $(seq 0 $((J-1))); do
  A=$(( NF * i / J )); B=$(( NF * (i+1) / J ))
  python3 -m anim.render range $A $B build/chunks/c$i.mp4 > build/chunks/log$i.txt 2>&1 &
  PIDS+=($!)
  echo "file 'c$i.mp4'" >> build/chunks/list.txt
done
for p in "${PIDS[@]}"; do wait $p; done
ffmpeg -loglevel error -y -f concat -safe 0 -i build/chunks/list.txt -c copy build/video_only.mp4
tools/final_encode.sh
echo done $NF
