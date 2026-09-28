"""Core drawing toolkit: paper textures, hand-drawn lines, cut-paper shapes, text, easing."""
import math, os, functools
import numpy as np
import cairo

W, H, FPS = 1920, 1080, 24
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "build", "tex")
os.makedirs(TEX, exist_ok=True)

# ---------------------------------------------------------------- palette
def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

PAPER = hexc('F0E7D6')
PAPER_D = hexc('E4D8C2')
CREAM = hexc('FAF4E8')
INK = hexc('2E2926')
INK_SOFT = hexc('5A514B')
RED = hexc('B04A3A')
RED_D = hexc('7E2E2A')
RED_L = hexc('D98C78')
BLUSH = hexc('E8B9A6')
OCHRE = hexc('D39A45')
OCHRE_L = hexc('E9C27E')
TEAL = hexc('3F6F6C')
TEAL_L = hexc('86ADA6')
SLATE = hexc('5B7690')
SLATE_L = hexc('A9BCCB')
SAGE = hexc('8FA07A')
BONE = hexc('EFE3CB')

def with_a(c, a): return (c[0], c[1], c[2], a)
def mix(c1, c2, t): return tuple(c1[i] * (1 - t) + c2[i] * t for i in range(4))

# ---------------------------------------------------------------- easing / timing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def ease(t):  # cubic in-out
    t = clamp(t); return 4 * t * t * t if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def eout(t):
    t = clamp(t); return 1 - (1 - t) ** 3
def ein(t):
    t = clamp(t); return t * t * t
def eback(t, s=1.4):
    t = clamp(t); t -= 1; return t * t * ((s + 1) * t + s) + 1
def ph(t, t0, d=0.6, fn=eout):
    """phase 0..1 starting at t0 over d seconds"""
    return fn((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)
def win(t, t0, t1, fin=0.5, fout=0.5):
    """1 inside [t0,t1] with fades"""
    return min(ph(t, t0, fin, ease), 1 - ph(t, t1 - fout, fout, ease))
def keys(t, kf, fn=None):
    """keyframes [(time, value_or_tuple), ...] with eased interpolation"""
    fn = fn or ease
    if t <= kf[0][0]: return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t < t1:
            p = fn((t - t0) / (t1 - t0)) if t1 > t0 else 1
            if isinstance(v0, tuple): return tuple(lerp(a, b, p) for a, b in zip(v0, v1))
            return lerp(v0, v1, p)
    return kf[-1][1]

def lerp_pt(a, b, t): return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))

# ---------------------------------------------------------------- noise
_rng = np.random.default_rng(7)
_perm = _rng.random(4096)
def vnoise(x, seed=0):
    """smooth 1D value noise in [-1,1]"""
    x = x + seed * 17.13
    i = math.floor(x); f = x - i
    a = _perm[i % 4096]; b = _perm[(i + 1) % 4096]
    f = f * f * (3 - 2 * f)
    return (a + (b - a) * f) * 2 - 1

def fbm(x, seed=0):
    return vnoise(x, seed) * .65 + vnoise(x * 2.3, seed + 3) * .25 + vnoise(x * 5.1, seed + 9) * .1

# boil: hand-drawn line boil updates on "threes" (8 fps)
_frame = [0]
def set_frame(f): _frame[0] = f
def boil(): return _frame[0] // 3

# ---------------------------------------------------------------- geometry
def poly_len(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))

def resample(pts, step=6.0, closed=False):
    if closed: pts = list(pts) + [pts[0]]
    out = [pts[0]]; carry = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; d = math.dist(a, b)
        if d == 0: continue
        t = step - carry
        while t <= d:
            out.append((a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d)); t += step
        carry = d - (t - step)
    if math.dist(out[-1], pts[-1]) > 0.5: out.append(pts[-1])
    if closed and len(out) > 2 and math.dist(out[-1], out[0]) < step * .5: out.pop()
    return out

def jitter(pts, amp=1.5, freq=0.02, seed=0, closed=False, step=5.0, boil_on=True):
    """offset points along normals with smooth noise; boils over time"""
    if len(pts) < 2: return pts
    p = resample(pts, step, closed)
    n = len(p); out = []
    s0 = seed * 3.7 + (boil() * 11.3 if boil_on else 0)
    acc = 0.0
    for i in range(n):
        a = p[i - 1] if (i > 0 or closed) else p[i]
        b = p[(i + 1) % n] if (i < n - 1 or closed) else p[i]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if i > 0: acc += math.dist(p[i], p[i - 1])
        o = fbm(acc * freq, s0) * amp
        out.append((p[i][0] + nx * o, p[i][1] + ny * o))
    return out

def bez(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n; mt = 1 - t
        pts.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return pts

def qbez(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]

def catmull(pts, n=10, closed=False):
    """smooth curve through points"""
    P = list(pts)
    if closed: P = [P[-1]] + P + [P[0], P[1]]
    else: P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    if not closed: out.append(P[-2])
    return out

def ellipse_pts(cx, cy, rx, ry, n=64, rot=0.0, a0=0.0, a1=2 * math.pi):
    c, s = math.cos(rot), math.sin(rot); out = []
    for i in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1)):
        a = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out

def rect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

def rrect_pts(x, y, w, h, r, n=6):
    pts = []
    for cx, cy, a0 in [(x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0), (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)]:
        for i in range(n + 1):
            a = a0 + (math.pi / 2) * i / n; pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def xform(pts, tx=0, ty=0, sc=1.0, rot=0.0, ox=0, oy=0):
    c, s = math.cos(rot), math.sin(rot); out = []
    for x, y in pts:
        x, y = (x - ox) * sc, (y - oy) * sc
        out.append((x * c - y * s + ox + tx, x * s + y * c + oy + ty))
    return out

def partial(pts, frac):
    """first frac of a polyline by length"""
    if frac >= 1: return pts
    if frac <= 0 or len(pts) < 2: return pts[:1]
    L = poly_len(pts) * frac; acc = 0; out = [pts[0]]
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if acc + d >= L:
            t = (L - acc) / d if d else 0
            out.append(lerp_pt(pts[i], pts[i + 1], t)); return out
        acc += d; out.append(pts[i + 1])
    return out

def point_at(pts, frac):
    q = partial(pts, clamp(frac)); return q[-1]

def angle_at(pts, frac):
    q = partial(pts, clamp(frac, 0.001, 1))
    if len(q) < 2: return 0
    a, b = q[-2], q[-1]; return math.atan2(b[1] - a[1], b[0] - a[0])

# ---------------------------------------------------------------- textures
def _smooth_noise(h, w, scale, rng):
    gh, gw = h // scale + 3, w // scale + 3
    g = rng.random((gh, gw)).astype(np.float32)
    from scipy.ndimage import zoom
    z = zoom(g, scale, order=3)[:h, :w]
    return z

def _make_textures():
    from PIL import Image
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(11)
    ph_, pw_ = 1300, 2300
    base = np.array(PAPER[:3], np.float32) * 255
    blotch = _smooth_noise(ph_, pw_, 180, rng) - .5
    mid = _smooth_noise(ph_, pw_, 40, rng) - .5
    fine = rng.normal(0, 1, (ph_, pw_)).astype(np.float32)
    fibers = gaussian_filter(rng.normal(0, 1, (ph_, pw_)).astype(np.float32), sigma=(0.6, 5.0))
    fibers2 = gaussian_filter(rng.normal(0, 1, (ph_, pw_)).astype(np.float32), sigma=(4.0, 0.7))
    lum = blotch * 9 + mid * 5 + fine * 2.4 + fibers * 8 + fibers2 * 4.5
    img = np.clip(base[None, None, :] + lum[..., None] * np.array([1.0, 0.95, 0.85]), 0, 255)
    # sparse speckles
    sp = rng.random((ph_, pw_)) > 0.9993
    img[sp] *= 0.78
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(TEX, "paper.png"))
    # grain texture for cut-paper fills (grayscale around mid gray)
    gh_, gw_ = 1024, 1024
    g = 128 + gaussian_filter(rng.normal(0, 1, (gh_, gw_)), 0.7) * 16 + (_smooth_noise(gh_, gw_, 60, rng) - .5) * 40 \
        + gaussian_filter(rng.normal(0, 1, (gh_, gw_)), (0.5, 3)) * 14
    g = np.clip(g, 0, 255).astype(np.uint8)
    Image.fromarray(np.stack([g, g, g], -1)).save(os.path.join(TEX, "grain.png"))
    # film grain frames
    for k in range(6):
        n = gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), 0.55)
        np.save(os.path.join(TEX, "fg%d.npy" % k), (n * 5).astype(np.int8))
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .66)) ** 2)
    v = 1 - 0.20 * np.clip(r - .45, 0, 1) ** 1.6
    np.save(os.path.join(TEX, "vig.npy"), v.astype(np.float32))

@functools.lru_cache(None)
def tex(name):
    p = os.path.join(TEX, name + ".png")
    if not os.path.exists(p): _make_textures()
    return cairo.ImageSurface.create_from_png(p)

@functools.lru_cache(None)
def post_data():
    if not os.path.exists(os.path.join(TEX, "vig.npy")): _make_textures()
    fg = [np.load(os.path.join(TEX, "fg%d.npy" % k)).astype(np.int16) for k in range(6)]
    vig = np.load(os.path.join(TEX, "vig.npy"))
    return fg, vig

# ---------------------------------------------------------------- drawing primitives
def path(ctx, pts, closed=False):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    if closed: ctx.close_path()

def set_c(ctx, c, a=1.0): ctx.set_source_rgba(c[0], c[1], c[2], c[3] * a)

def paper_bg(ctx, dx=0, dy=0):
    s = tex("paper")
    ctx.save(); ctx.set_source_surface(s, -150 + dx, -100 + dy); ctx.paint(); ctx.restore()

def grain_fill(ctx, strength=0.55, op=cairo.OPERATOR_SOFT_LIGHT, ox=0, oy=0):
    """call with a clip/path already set: overlays paper grain"""
    s = tex("grain")
    pat = cairo.SurfacePattern(s); pat.set_extend(cairo.EXTEND_REPEAT)
    m = cairo.Matrix(); m.translate(ox, oy); pat.set_matrix(m)
    ctx.save(); ctx.set_operator(op); ctx.set_source(pat); ctx.paint_with_alpha(strength); ctx.restore()

def ink(ctx, pts, w=2.4, c=INK, a=1.0, prog=1.0, seed=0, amp=1.1, closed=False, sketch=True, cap=cairo.LINE_CAP_ROUND, dash=None):
    if a <= 0.003 or prog <= 0 or len(pts) < 2: return
    p = jitter(pts, amp, 0.018, seed, closed and prog >= 1)
    if prog < 1: p = partial(p, prog)
    if len(p) < 2: return
    ctx.save(); ctx.set_line_cap(cap); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash: ctx.set_dash(dash)
    set_c(ctx, c, a); ctx.set_line_width(w); path(ctx, p, closed and prog >= 1); ctx.stroke()
    if sketch:  # faint second pass, like a pencil re-trace
        p2 = jitter(pts, amp * 1.6, 0.03, seed + 50, closed and prog >= 1)
        if prog < 1: p2 = partial(p2, prog)
        set_c(ctx, c, a * 0.28); ctx.set_line_width(max(0.8, w * 0.45)); path(ctx, p2, closed and prog >= 1); ctx.stroke()
    ctx.restore()

def paper_shape(ctx, pts, fill, a=1.0, seed=0, shadow=0.22, sh_off=(5, 7), edge=True, grain=0.95, amp=1.6,
                outline=None, ow=2.0, hatch=None, hatch_a=0.2, hatch_sp=9, hatch_ang=0.8, rim=True, shade=0.18, shade_dir=(0.3, 1.0)):
    """cut-paper shape with soft shadow, grain, paper-edge rim, optional ink outline & hatching"""
    if a <= 0.003 or len(pts) < 3: return
    p = jitter(pts, amp, 0.035, seed, True, step=6)
    ctx.save()
    if shadow > 0:
        for k, (m, al) in enumerate([(1.0, .45), (0.6, .35), (1.4, .2)]):
            ctx.save(); ctx.translate(sh_off[0] * m, sh_off[1] * m)
            ctx.set_source_rgba(0.18, 0.12, 0.09, shadow * al * a); path(ctx, p, True); ctx.fill(); ctx.restore()
    path(ctx, p, True); ctx.save(); ctx.clip()
    set_c(ctx, fill, a); ctx.paint()
    if grain: grain_fill(ctx, grain * a, ox=seed * 37 % 500, oy=seed * 53 % 500)
    if shade:
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2; rr = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
        g = cairo.LinearGradient(cx - shade_dir[0] * rr, cy - shade_dir[1] * rr, cx + shade_dir[0] * rr, cy + shade_dir[1] * rr)
        g.add_color_stop_rgba(0, 1, 1, 1, shade * .8 * a); g.add_color_stop_rgba(.5, 1, 1, 1, 0); g.add_color_stop_rgba(.5, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, .1, .05, .03, shade * a)
        ctx.set_source(g); ctx.paint()
    if hatch:
        set_c(ctx, hatch, hatch_a * a); ctx.set_line_width(1.1)
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); span = (x1 - x0) + (y1 - y0)
        k = 0; d = -span
        while d < span:
            q0 = (x0 + d, y1); q1 = (x0 + d + (y1 - y0) * hatch_ang, y0)
            ln = jitter([q0, q1], 0.8, 0.05, seed + k, boil_on=False, step=12)
            path(ctx, ln); ctx.stroke(); d += hatch_sp; k += 1
    ctx.restore()
    if rim and edge:
        ctx.set_line_width(1.3); set_c(ctx, CREAM, 0.45 * a); path(ctx, p, True); ctx.stroke()
    if outline:
        ink(ctx, pts, ow, outline, a, seed=seed + 7, closed=True)
    ctx.restore()

def dots(ctx, pts, r, c, a=1.0):
    set_c(ctx, c, a)
    for x, y in pts: ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

def blob(ctx, x, y, r, c, a=1.0, seed=0, grain=0.5, shadow=0.18, outline=None, ow=1.6, squash=1.0, rot=0.0):
    paper_shape(ctx, ellipse_pts(x, y, r, r * squash, max(16, int(r)), rot), c, a, seed, shadow=shadow,
                sh_off=(r * .06 + 1, r * .09 + 1.5), grain=grain, amp=max(0.5, r * .03), outline=outline, ow=ow)

def glow(ctx, x, y, r, c, a=1.0):
    if a <= 0: return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], .55 * a); g.add_color_stop_rgba(.4, c[0], c[1], c[2], .22 * a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.save(); ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill(); ctx.restore()

def arrow(ctx, pts, w=2.6, c=INK, a=1.0, prog=1.0, seed=0, head=16, both=False):
    if prog <= 0 or a <= 0: return
    ink(ctx, pts, w, c, a, prog, seed)
    def headat(frac, back=False):
        tip = point_at(pts, frac); ang = angle_at(pts, frac) + (math.pi if back else 0)
        if back: tip = pts[0]; ang = math.atan2(pts[0][1] - pts[1][1], pts[0][0] - pts[1][0])
        l = (tip[0] - head * math.cos(ang - .45), tip[1] - head * math.sin(ang - .45))
        r = (tip[0] - head * math.cos(ang + .45), tip[1] - head * math.sin(ang + .45))
        ink(ctx, [l, tip, r], w, c, a, seed=seed + 3, sketch=False)
    if prog > 0.05: headat(prog)
    if both and prog > 0.05: headat(0, True)

# ---------------------------------------------------------------- text
FONTS = {
    'title': ("DM Serif Display", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
    'title_i': ("DM Serif Display", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL),
    'serif': ("EB Garamond", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
    'serif_i': ("EB Garamond", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL),
    'hand': ("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
    'hand_b': ("Kalam", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
    'sans': ("Work Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
    'sans_b': ("Work Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
}

def set_font(ctx, font, size):
    f, sl, wt = FONTS[font]; ctx.select_font_face(f, sl, wt); ctx.set_font_size(size)

def text_w(ctx, s, font, size):
    set_font(ctx, font, size); return ctx.text_extents(s).x_advance

def text(ctx, s, x, y, font='hand', size=40, c=INK, a=1.0, align='left', reveal=1.0, rot=0.0, spacing=0.0, rise=0.0):
    """baseline text; reveal wipes in left->right with soft edge"""
    if a <= 0.003 or reveal <= 0: return
    set_font(ctx, font, size)
    if spacing:
        wdt = sum(ctx.text_extents(ch).x_advance + spacing for ch in s) - spacing
    else:
        wdt = ctx.text_extents(s).x_advance
    ox = {'left': 0, 'center': -wdt / 2, 'right': -wdt}[align]
    ctx.save(); ctx.translate(x, y + (1 - reveal) * rise); ctx.rotate(rot)
    if reveal < 1:
        ctx.push_group()
    set_c(ctx, c, a)
    if spacing:
        cx = ox
        for ch in s:
            ctx.move_to(cx, 0); ctx.show_text(ch); cx += ctx.text_extents(ch).x_advance + spacing
    else:
        ctx.move_to(ox, 0); ctx.show_text(s)
    if reveal < 1:
        ctx.pop_group_to_source()
        e = size * 1.2
        pos = ox - e + (wdt + 2 * e) * reveal
        g = cairo.LinearGradient(pos - e, 0, pos, 0)
        g.add_color_stop_rgba(0, 0, 0, 0, 1); g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.mask(g)
    ctx.restore()
    return wdt

def label(ctx, s, x, y, tx, ty, t, t0, font='hand', size=34, c=INK, a=1.0, align='left', seed=0, dur=0.7, dot=True):
    """leader line from point (tx,ty) to text anchor (x,y), drawn on at t0"""
    p = ph(t, t0, dur, ease)
    if p <= 0 or a <= 0: return
    ex = x - 10 if align == 'left' else x + 10 if align == 'right' else x
    ey = y - size * .32
    mid = ((tx + ex) / 2, (ty + ey) / 2 - 12)
    ln = qbez((tx, ty), mid, (ex, ey), 16)
    ink(ctx, ln, 1.7, c, a * .85, prog=clamp(p * 1.6), seed=seed)
    if dot: dots(ctx, [(tx, ty)], 4.2 * ph(t, t0, .25), c, a)
    text(ctx, s, x + (6 if align == 'left' else -6 if align == 'right' else 0), y, font, size, c, a, align, reveal=clamp(p * 1.4 - .3))

def underline(ctx, x0, x1, y, t, t0, c=RED, w=4, a=1.0, seed=0, dur=0.5):
    p = ph(t, t0, dur, ease)
    pts = [(x0, y + 2), ((x0 + x1) / 2, y - 3), (x1, y + 1)]
    ink(ctx, catmull(pts, 12), w, c, a * .9, prog=p, seed=seed, amp=1.5)

def circle_mark(ctx, cx, cy, rx, ry, t, t0, c=RED, w=3.2, a=1.0, seed=0, dur=0.7):
    p = ph(t, t0, dur, ease)
    pts = ellipse_pts(cx, cy, rx, ry, 60, -.12, -2.2, -2.2 + 2 * math.pi * 1.08)
    ink(ctx, pts, w, c, a, prog=p, seed=seed, amp=2.5)

# ---------------------------------------------------------------- compositing / post
def new_surface():
    return cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)

def post(surface, frame):
    """film grain + vignette + tiny exposure flicker; returns RGB bytes (bgra layout kept for ffmpeg)"""
    surface.flush()
    buf = np.ndarray((H, W, 4), np.uint8, surface.get_data())
    fg, vig = post_data()
    g = fg[frame % 6]
    flick = 1.0 + 0.006 * vnoise(frame * 0.35, 99)
    img = buf[..., :3].astype(np.float32) * (vig[..., None] * flick) + g[..., None]
    out = np.empty((H, W, 4), np.uint8); out[..., :3] = np.clip(img, 0, 255); out[..., 3] = 255
    return out.tobytes()
