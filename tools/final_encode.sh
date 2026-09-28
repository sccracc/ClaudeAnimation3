#!/bin/bash
# Two-pass H.264 encode of the rendered frames + soundtrack, sized to stay under 100 MB.
set -e
cd "$(dirname "$0")/.."
mkdir -p output
ffmpeg -loglevel error -y -i build/video_only.mp4 -c:v libx264 -preset slow -tune animation -b:v 2400k -pass 1 -passlogfile build/x264 -pix_fmt yuv420p -r 24 -an -f null /dev/null
ffmpeg -loglevel error -y -i build/video_only.mp4 -i build/mix.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -tune animation -b:v 2400k -maxrate 6000k -bufsize 12000k -pass 2 -passlogfile build/x264 \
  -pix_fmt yuv420p -profile:v high -level 4.1 -r 24 \
  -af "volume=3.2dB,alimiter=limit=0.89:level=false" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart -shortest output/animated-short-final.mp4
ls -la output/animated-short-final.mp4
