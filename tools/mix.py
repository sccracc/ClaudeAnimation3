"""Build the final soundtrack: narration + ducked music + procedural paper/whoosh sfx."""
import sys, json, wave, numpy as np
sys.path.insert(0, '.')
from scipy.signal import butter, sosfilt, sosfiltfilt
from anim.render import timeline, OVER
SR = 48000

def rd(p):
    w = wave.open(p); n = w.getnframes(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    x = x.reshape(-1, ch)
    if ch == 1: x = np.repeat(x, 2, 1)
    assert w.getframerate() == SR
    return x

def db(x): return 10 ** (x / 20)
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)

tl = timeline()
T = tl[-1]["end"]; N = int(T * SR) + SR
vo = np.zeros((N, 2), np.float32); pres = np.zeros(N, np.float32)
hp = butter(2, 70, 'hp', fs=SR, output='sos')
for it in tl:
    sc = it["scene"]
    if not sc.sid: continue
    x = rd("audio/vo/%s.wav" % sc.sid)
    x = sosfilt(hp, x, axis=0)
    # per-section loudness match (speech-active RMS)
    env = np.abs(x[:, 0]); act = x[env > 0.02, 0]
    x = x * (db(-20) / rms(act))
    st = int((it["start"] + sc.lead) * SR)
    vo[st:st + len(x)] += x
    pres[st:st + len(x)] = 1.0
# smooth presence -> ducking envelope (fast attack, slow release)
k = int(0.5 * SR)
from scipy.ndimage import maximum_filter1d, uniform_filter1d
pres = maximum_filter1d(pres, int(0.8 * SR))
pres = uniform_filter1d(pres, k)

# music: track1 from 0, track2 aligned so it ends at the film end, crossfade
m1 = rd("audio/music/lyria1.wav"); m2 = rd("audio/music/lyria2.wav")
mus = np.zeros((N, 2), np.float32)
x2s = int((T + 0.5) * SR) - len(m2)
xf = int(9 * SR)
l1 = min(len(m1), x2s + xf)
g1 = np.ones(l1, np.float32); g1[x2s:l1] = np.cos(np.linspace(0, np.pi / 2, l1 - x2s)) ** 1
mus[:l1] += m1[:l1] * g1[:, None]
g2 = np.ones(len(m2), np.float32); g2[:xf] = np.sin(np.linspace(0, np.pi / 2, xf))
e2 = min(N, x2s + len(m2)); mus[x2s:e2] += (m2 * g2[:, None])[:e2 - x2s]
# gentle fade-in at the very start and fade-out at the end
fi = int(1.5 * SR); mus[:fi] *= np.linspace(0, 1, fi)[:, None]
end = int(T * SR); fo = int(3.0 * SR); mus[end - fo:end] *= np.linspace(1, 0, fo)[:, None]; mus[end:] = 0
# carve a little space for the voice: dip 1-4 kHz under narration
bp = butter(2, [1200, 4000], 'bp', fs=SR, output='sos')
mid = sosfilt(bp, mus, axis=0)
mus = mus - mid * (0.45 * pres)[:, None]
mref = rms(mus[: int(170 * SR)])
mus = mus * (db(-27) / mref)
duck = db(-9) * pres + 1.0 * (1 - pres)   # music ~9 dB lower under the voice
mus *= duck[:, None]

# ---- procedural sfx
rng = np.random.default_rng(1)
sfx = np.zeros((N, 2), np.float32)
def rustle(t0, dur=0.8, lvl=-31, pan=0.0):
    n = int(dur * SR); x = rng.normal(0, 1, n).astype(np.float32)
    x = sosfilt(butter(2, [900, 7000], 'bp', fs=SR, output='sos'), x)
    crackle = np.abs(sosfilt(butter(1, 30, 'lp', fs=SR, output='sos'), rng.normal(0, 1, n))) * 3
    envl = np.minimum(1, np.linspace(0, 1, n) / 0.12) * np.exp(-np.linspace(0, 1, n) * 3.2)
    x = x * (0.5 + crackle) * envl; x = x / (np.max(np.abs(x)) + 1e-9) * db(lvl)
    st = int(t0 * SR); e = min(N, st + n)
    L = np.linspace(0.5 - pan, 0.5 + pan, n)[:e - st]
    sfx[st:e, 0] += x[:e - st] * (1 - L) * 1.4; sfx[st:e, 1] += x[:e - st] * L * 1.4
def whoosh(t0, dur=1.3, lvl=-30, up=True):
    n = int(dur * SR); x = rng.normal(0, 1, n).astype(np.float32)
    out = np.zeros(n, np.float32); blk = 1024
    zi = None
    for i in range(0, n, blk):
        f = 250 + 2800 * ((i / n) if up else (1 - i / n)) ** 1.5
        sos = butter(2, f, 'lp', fs=SR, output='sos')
        out[i:i + blk] = sosfilt(sos, x[i:i + blk])
    envl = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    out = out * envl; out = out / (np.max(np.abs(out)) + 1e-9) * db(lvl)
    st = int(t0 * SR); e = min(N, st + n)
    sfx[st:e] += np.stack([out, out], 1)[:e - st]
for i, it in enumerate(tl):
    if i > 0:
        rustle(it["start"] - 0.05, 0.9, -30, pan=0.25 if it["trans"] != 'up' else 0.0)
    sc = it["scene"]
    if hasattr(sc, "sfx"):
        for lt, kind in sc.sfx():
            whoosh(it["start"] + lt, 1.3, -31, up=(kind == 'zoom'))
# soft reverb-ish smear on sfx
sfx = sfx + 0.3 * np.roll(sfx, int(0.043 * SR), 0) + 0.18 * np.roll(sfx, int(0.089 * SR), 0)

mix = vo + mus + sfx
mix = mix[:int(T * SR)]
peak = np.max(np.abs(mix)); print("peak", peak, "dur", len(mix) / SR)
# soft limiter
mix = np.tanh(mix / 0.95) * 0.95 if peak > 0.9 else mix
out = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
w = wave.open("build/mix.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
np.save("build/pres.npy", pres[::480])
print("ok")
