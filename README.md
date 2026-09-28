# Under Tension — What Actually Happens to Your Muscles When You Work Out

A 4 min 47 s animated documentary short in a hand-drawn paper-collage style.

**Final video:** `output/animated-short-final.mp4` (1920×1080, 24 fps, H.264 + AAC)

## How it was made

Everything is generated from code in this repository, except the narration and the two music tracks, which come from the OpenRouter API.

| Part | How |
| --- | --- |
| Script | `script/script.json`: 10 narrated sections |
| Narration | MiniMax Speech 2.8 HD (`English_expressive_narrator`, speed 0.93) through OpenRouter (`tools/orclient.py`) |
| Word timing | Speech pauses detected in the audio and matched to punctuation (`tools/align.py`, `tools/align2.py`) → `script/timing.json` |
| Music | Two Google Lyria 3 Pro pieces in F major, crossfaded (`tools/lyria.py`) |
| Visuals | Procedural 2D animation in pycairo: paper textures, cut-paper shapes, boiling ink lines, loupe zooms, torn-paper sheet transitions (`anim/`) |
| Sound design | Procedural paper rustles and soft whooshes; music is ducked under the voice (`tools/mix.py`) |
| Render | `tools/render_all.sh` renders in parallel chunks, then muxes with the mix |

## Rebuild

```bash
pip install pycairo numpy scipy pillow imageio-ffmpeg
# fonts in assets/fonts must be installed (e.g. copy them to ~/.fonts and run fc-cache)
python3 tools/align2.py          # word timings from the narration audio
python3 tools/mix.py             # soundtrack -> build/mix.wav
tools/render_all.sh              # frames -> output/animated-short-final.mp4
python3 -m anim.render png 42.5  # preview a single frame
```

Rebuilding needs the narration WAVs. Regenerate them from the MP3s in `audio/vo/` with
`ffmpeg -i X.mp3 -ar 48000 -ac 1 X.wav`, and do the same for the music (use `-ac 2`).
