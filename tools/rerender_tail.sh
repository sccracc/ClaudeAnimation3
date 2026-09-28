#!/bin/bash
# Re-render only chunks 2-3 (second half) and rebuild the final file.
set -e
cd "$(dirname "$0")/.."
A=$(sed -n 's/.*\[\([0-9]*\)-.*/\1/p' build/chunks/log2.txt | head -1)
B=$(python3 -c "import sys;sys.path.insert(0,'.');from anim.render import total_frames;print(total_frames())")
for k in 0 1 2 3; do a=$((A+(B-A)*k/4)); b=$((A+(B-A)*(k+1)/4)); python3 -m anim.render range $a $b build/chunks/t$k.mp4 > build/chunks/logt$k.txt 2>&1 & done
wait
printf "file 'c0.mp4'\nfile 'c1.mp4'\nfile 't0.mp4'\nfile 't1.mp4'\nfile 't2.mp4'\nfile 't3.mp4'\n" > build/chunks/list2.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i build/chunks/list2.txt -c copy build/video_only.mp4
tools/final_encode.sh
echo done
