"""Timeline assembly, transitions, frame rendering and parallel encoding."""
import sys, os, subprocess, json, time
from .core import *
from . import scenes as SC

OVER = 1.0  # transition overlap (s)

def build_timeline():
    seq = SC.sequence()
    out = []; t = 0.0
    for i, (scene, trans) in enumerate(seq):
        out.append({"scene": scene, "start": t, "end": t + scene.dur, "trans": trans})
        t = t + scene.dur - (OVER if i + 1 < len(seq) and seq[i + 1][1] != 'cut' else 0)
    return out

TL = None
def timeline():
    global TL
    if TL is None: TL = build_timeline()
    return TL

def total_frames():
    tl = timeline(); return int(math.ceil(tl[-1]["end"] * FPS))

def _draw_scene(item, t, surf=None):
    s = surf or new_surface(); ctx = cairo.Context(s)
    item["scene"].draw(ctx, t - item["start"])
    return s

def torn_edge(x, p, seed, vertical=True, h=H, jag=18):
    pts = []
    n = 60
    for i in range(n + 1):
        y = -40 + (h + 80) * i / n
        off = fbm(i * .35, seed) * jag + vnoise(i * 2.7, seed + 5) * 5
        pts.append((x + off, y))
    return pts

def composite(sA, sB, p, style, seed):
    """sheet transition: B is a new paper sheet sliding over A"""
    out = new_surface(); ctx = cairo.Context(out)
    ctx.set_source_surface(sA, 0, 0); ctx.paint()
    pe = ease(p)
    if style == 'fade':
        ctx.set_source_surface(sB, 0, 0); ctx.paint_with_alpha(pe); return out
    if style == 'up':
        y = H + 60 - (H + 140) * pe
        edge = [(q[1] * W / H * 1.0 - 40 * W / H, q[0] - 0) for q in []]
        pts = []
        for i in range(61):
            xx = -40 + (W + 80) * i / 60
            pts.append((xx, y + fbm(i * .35, seed) * 18 + vnoise(i * 2.7, seed + 5) * 5))
        poly = pts + [(W + 40, H + 60), (-40, H + 60)]
        # shadow on A
        for k, al in [(18, .10), (10, .12), (5, .14)]:
            ctx.save(); ctx.translate(0, -k); path(ctx, poly, True); ctx.set_source_rgba(.15, .1, .08, al); ctx.fill(); ctx.restore()
        ctx.save(); path(ctx, poly, True); ctx.clip()
        ctx.set_source_surface(sB, 0, (1 - pe) * 90); ctx.paint(); ctx.restore()
        ink(ctx, pts, 2.4, CREAM, .9, seed=seed, sketch=False, amp=.5)
        return out
    # default: from the right
    x = W + 60 - (W + 140) * pe
    pts = torn_edge(x, pe, seed)
    poly = pts + [(W + 60, H + 40), (W + 60, -40)]
    for k, al in [(22, .08), (12, .11), (5, .14)]:
        ctx.save(); ctx.translate(-k, 0); path(ctx, poly, True); ctx.set_source_rgba(.15, .1, .08, al); ctx.fill(); ctx.restore()
    ctx.save(); path(ctx, poly, True); ctx.clip()
    ctx.set_source_surface(sB, (1 - pe) * 160, 0); ctx.paint(); ctx.restore()
    ink(ctx, pts, 2.4, CREAM, .9, seed=seed, sketch=False, amp=.5)
    return out

def render_frame(n):
    set_frame(n)
    t = n / FPS
    tl = timeline()
    act = [i for i, it in enumerate(tl) if it["start"] <= t < it["end"]]
    if not act: act = [len(tl) - 1]
    if len(act) == 1:
        return _draw_scene(tl[act[0]], t)
    a, b = act[0], act[-1]
    sA = _draw_scene(tl[a], t); sB = _draw_scene(tl[b], t)
    p = (t - tl[b]["start"]) / OVER
    return composite(sA, sB, clamp(p), tl[b]["trans"], seed=b * 13)

def save_png(n, path_):
    from PIL import Image
    s = render_frame(n); b = post(s, n)
    a = np.frombuffer(b, np.uint8).reshape(H, W, 4)[..., [2, 1, 0]]
    Image.fromarray(a).save(path_)

FF = "ffmpeg"

def encode_range(f0, f1, out):
    cmd = [FF, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(f0, f1):
        s = render_frame(n); p.stdin.write(post(s, n))
        if (n - f0) % 240 == 0: print("  [%d-%d] frame %d  %.1fs" % (f0, f1, n, time.time() - t0), flush=True)
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "info":
        for it in timeline():
            print("%-18s %7.2f %7.2f  dur %.2f vo@%.2f" % (type(it["scene"]).__name__, it["start"], it["end"], it["scene"].dur, it["start"] + it["scene"].lead))
        print("total", timeline()[-1]["end"])
    elif mode == "png":
        for tt in sys.argv[2:]:
            n = int(float(tt) * FPS); save_png(n, os.path.join(ROOT, "build", "prev", "f_%06.2f.png" % float(tt)))
    elif mode == "range":
        encode_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
