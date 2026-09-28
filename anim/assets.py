"""Reusable illustrated props and diagram pieces."""
from .core import *

def dumbbell_icon(ctx, x, y, s=1.0, a=1.0, seed=0, rot=0.0, col=INK_SOFT):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    paper_shape(ctx, rect_pts(-70, -7, 140, 14), mix(col, PAPER, .25), a, seed, shadow=.15, amp=.6)
    for sx in (-1, 1):
        paper_shape(ctx, rrect_pts(sx * 58 - 13, -40, 26, 80, 6), col, a, seed + 1 + sx, shadow=.2, amp=.7)
        paper_shape(ctx, rrect_pts(sx * 80 - 9, -30, 18, 60, 5), mix(col, INK, .3), a, seed + 3 + sx, shadow=.2, amp=.7)
    ctx.restore()

def moon_icon(ctx, x, y, r=60, a=1.0, seed=0, col=OCHRE_L):
    outer = ellipse_pts(x, y, r, r, 60)
    ctx.save()
    ctx.push_group()
    set_c(ctx, col); path(ctx, jitter(outer, 1, .03, seed, True), True); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR); path(ctx, ellipse_pts(x + r * .45, y - r * .25, r * .85, r * .85, 60), True); ctx.fill()
    g = ctx.pop_group()
    ctx.save(); ctx.translate(4, 6); ctx.set_source_rgba(.15, .1, .08, .2 * a); ctx.mask(g); ctx.restore()
    ctx.set_source(g); ctx.paint_with_alpha(a)
    ctx.restore()
    for i, (dx, dy, rr) in enumerate([(r * 1.2, -r * .9, 7), (r * 1.6, -r * .1, 5), (r * .9, r * .2, 4)]):
        star(ctx, x + dx, y + dy, rr, col, a, seed + i)

def star(ctx, x, y, r, c, a=1.0, seed=0):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .45
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    paper_shape(ctx, pts, c, a, seed, shadow=.1, amp=.3, grain=.5)

def clock_icon(ctx, x, y, r, t_hand, a=1.0, seed=0):
    blob(ctx, x, y, r, CREAM, a, seed, outline=INK, ow=2.2)
    for k in range(12):
        ang = k * math.pi / 6
        ink(ctx, [(x + math.cos(ang) * r * .78, y + math.sin(ang) * r * .78), (x + math.cos(ang) * r * .88, y + math.sin(ang) * r * .88)], 2, INK, a, sketch=False)
    ang = -math.pi / 2 + t_hand * 2 * math.pi
    ink(ctx, [(x, y), (x + math.cos(ang) * r * .7, y + math.sin(ang) * r * .7)], 3, RED, a, sketch=False)
    ang2 = -math.pi / 2 + t_hand * 2 * math.pi / 12
    ink(ctx, [(x, y), (x + math.cos(ang2) * r * .45, y + math.sin(ang2) * r * .45)], 3.6, INK, a, sketch=False)
    dots(ctx, [(x, y)], 4, INK, a)

def plate_icon(ctx, x, y, r, a=1.0, seed=0):
    blob(ctx, x, y, r, CREAM, a, seed, outline=INK_SOFT, ow=1.8)
    ink(ctx, ellipse_pts(x, y, r * .72, r * .72, 40), 1.4, INK_SOFT, a * .6, seed=seed + 1, closed=True)
    # food: egg, beans, greens
    blob(ctx, x - r * .18, y - r * .12, r * .3, hexc('FBF6EC'), a, seed + 2, shadow=.1, outline=INK_SOFT, ow=1.2, squash=.8)
    blob(ctx, x - r * .18, y - r * .12, r * .12, OCHRE, a, seed + 3, shadow=.05)
    for i in range(5):
        blob(ctx, x + r * .28 + (i % 3) * r * .1, y + r * .15 + (i // 3) * r * .12, r * .07, RED_D, a, seed + 4 + i, shadow=.05, grain=.3)
    paper_shape(ctx, ellipse_pts(x + r * .2, y - r * .3, r * .22, r * .12, 20, .6), SAGE, a, seed + 9, shadow=.08)

def calendar_icon(ctx, x, y, w, h, a=1.0, seed=0, marks=None, t=0, t0=0):
    paper_shape(ctx, rect_pts(x, y, w, h), CREAM, a, seed, shadow=.18, outline=INK_SOFT, ow=1.6)
    paper_shape(ctx, rect_pts(x, y, w, h * .2), RED, a, seed + 1, shadow=0, amp=.5)
    cols, rows = 7, 4; cw = w / cols; rh = h * .8 / rows
    for r in range(rows):
        for c in range(cols):
            k = r * cols + c
            cx, cy = x + (c + .5) * cw, y + h * .2 + (r + .5) * rh
            dots(ctx, [(cx, cy)], 2.2, INK_SOFT, a * .5)
            if marks and k < len(marks):
                p = ph(t, t0 + k * .06, .3)
                if marks[k] == 'x' and p > 0:
                    ink(ctx, [(cx - 9, cy - 9), (cx + 9, cy + 9)], 2.6, RED, a, prog=p, seed=k, sketch=False)
                    ink(ctx, [(cx + 9, cy - 9), (cx - 9, cy + 9)], 2.6, RED, a, prog=p, seed=k + 50, sketch=False)
                elif marks[k] == 'o' and p > 0:
                    ink(ctx, ellipse_pts(cx, cy, 11, 11, 20), 2.4, TEAL, a, prog=p, seed=k, closed=True, sketch=False)

def tally(ctx, x, y, n, a=1.0, seed=0, c=INK, h=46, sp=15):
    for i in range(int(n)):
        g, k = divmod(i, 5)
        gx = x + g * (sp * 5 + 22)
        if k < 4:
            ink(ctx, [(gx + k * sp, y), (gx + k * sp + 3, y + h)], 3, c, a, seed=seed + i, sketch=False)
        else:
            ink(ctx, [(gx - 8, y + h * .75), (gx + 3 * sp + 10, y + h * .2)], 3, c, a, seed=seed + i, sketch=False)

def axes(ctx, x, y, w, h, t, t0, xl="", yl="", a=1.0, seed=0, c=INK):
    p = ph(t, t0, .8, ease)
    ink(ctx, [(x, y - h), (x, y)], 2.4, c, a, prog=p, seed=seed)
    arrowh = ph(t, t0 + .5, .3)
    ink(ctx, [(x, y), (x + w, y)], 2.4, c, a, prog=p, seed=seed + 1)
    if arrowh > 0:
        ink(ctx, [(x + w - 12, y - 8), (x + w, y), (x + w - 12, y + 8)], 2.4, c, a * arrowh, seed=seed + 2, sketch=False)
        ink(ctx, [(x - 8, y - h + 12), (x, y - h), (x + 8, y - h + 12)], 2.4, c, a * arrowh, seed=seed + 3, sketch=False)
    if xl: text(ctx, xl, x + w, y + 84, 'hand', 32, c, a, 'right', reveal=ph(t, t0 + .5, .7))
    if yl:
        ctx.save(); ctx.translate(x - 22, y - h); ctx.rotate(-math.pi / 2)
        text(ctx, yl, 0, 0, 'hand', 30, c, a, 'right', reveal=ph(t, t0 + .5, .7)); ctx.restore()

def curve(ctx, fn, x, y, w, h, t, t0, dur=1.2, c=RED, lw=3.4, a=1.0, seed=0, x0=0.0, x1=1.0, n=90):
    pts = [(x + w * (x0 + (x1 - x0) * i / n), y - h * fn(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]
    ink(ctx, pts, lw, c, a, prog=ph(t, t0, dur, ease), seed=seed, amp=.8)
    return pts

def particles(ctx, n, box, t, seed, r=6, c=OCHRE, a=1.0, speed=1.0, label=None, lsize=18, shape='dot'):
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    ps = rng.random((n, 4))
    for i in range(n):
        px = x0 + (x1 - x0) * ((ps[i, 0] + t * .03 * speed * (ps[i, 2] - .5)) % 1)
        py = y0 + (y1 - y0) * ((ps[i, 1] + t * .02 * speed * (ps[i, 3] - .5) + .03 * math.sin(t * 1.3 + i)) % 1)
        blob(ctx, px, py, r, c, a, seed + i, shadow=.12, grain=.4)
        if label:
            text(ctx, label, px, py + lsize * .35, 'sans_b', lsize, CREAM, a, 'center')

def zigzag(x, y0, y1, amp=10, n=8):
    pts = []
    for i in range(n + 1):
        pts.append((x + (amp if i % 2 else -amp), y0 + (y1 - y0) * i / n))
    return pts

def spring_pts(a, b, coils=8, amp=10):
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); L = math.dist(a, b)
    out = []
    for i in range(coils * 8 + 1):
        s = i / (coils * 8); off = math.sin(s * coils * 2 * math.pi) * amp
        out.append((a[0] + math.cos(ang) * L * s - math.sin(ang) * off, a[1] + math.sin(ang) * L * s + math.cos(ang) * off))
    return out

# ------------------------------------------------------------------ muscle structure pieces
def muscle_belly(ctx, x0, x1, cy, thick, a=1.0, seed=0, bulge=1.0, col=RED, stri=True, tendon=True):
    """horizontal muscle belly with tendons at both ends"""
    n = 40; top = []; bot = []
    for i in range(n + 1):
        s = i / n; x = lerp(x0, x1, s)
        w = thick * bulge * (math.sin(math.pi * s) ** .8) * .5 + 6
        top.append((x, cy - w + math.sin(s * math.pi) * 6)); bot.append((x, cy + w + math.sin(s * math.pi) * 6))
    shape = top + bot[::-1]
    if tendon:
        for (xa, xb) in [(x0 - 140, x0 + 30), (x1 - 30, x1 + 140)]:
            paper_shape(ctx, [(xa, cy - 9), (xb, cy - 6), (xb, cy + 8), (xa, cy + 10)], BONE, a, seed + 5, shadow=.15, outline=INK_SOFT, ow=1.3)
    paper_shape(ctx, shape, col, a, seed, shadow=.24, grain=1.0, shade=.25, shade_dir=(0, 1))
    if stri:
        for k in range(-5, 6):
            ln = [(lerp(x0, x1, s), cy + 6 * math.sin(s * math.pi) + k * (thick * bulge * .085) * (math.sin(math.pi * s) ** .8)) for s in [i / 30 for i in range(3, 28)]]
            ink(ctx, ln, 1.1, RED_D, .4 * a, seed=seed + 20 + k, sketch=False, amp=.7)
    ink(ctx, shape, 1.6, RED_D, .7 * a, seed=seed + 1, closed=True)
    return shape

_PACK = {}
def packed_circles(R, r, seed, count=400):
    """ring-packed circles with slight jitter (deterministic)"""
    key = (R, r, seed, count)
    if key in _PACK: return _PACK[key]
    rng = np.random.default_rng(seed); out = [(0.0, 0.0, r * (0.9 + .2 * rng.random()))]
    ring = 1
    while len(out) < count:
        rad = ring * r * 2.05
        if rad + r > R * 1.02: break
        m = int(2 * math.pi * rad / (r * 2.1))
        off = rng.random() * 6.28
        for k in range(m):
            ang = off + 2 * math.pi * k / m
            rr = r * (0.88 + .2 * rng.random())
            d = rad + (rng.random() - .5) * r * .25
            if d + rr <= R: out.append((math.cos(ang) * d, math.sin(ang) * d, rr))
        ring += 1
    _PACK[key] = out[:count]; return _PACK[key]

def cross_section(ctx, cx, cy, R, t, t0, a=1.0, seed=0, fibers_t=None, highlight=None):
    """muscle cross-section: outer sheath, fascicles, fibers"""
    p0 = ph(t, t0, .8, eback)
    if p0 <= 0: return []
    Rr = R * p0
    paper_shape(ctx, ellipse_pts(cx, cy, Rr + 14, Rr + 14, 90), CREAM, a, seed, shadow=.25)
    paper_shape(ctx, ellipse_pts(cx, cy, Rr, Rr, 90), mix(RED_L, CREAM, .3), a, seed + 1, shadow=0, grain=.8)
    fas = packed_circles(R * .95, R * .19, seed + 3, 30)
    shown = []
    for i, (x, y, r) in enumerate(fas):
        pi_ = ph(t, t0 + .5 + i * .08, .5, eback)
        if pi_ <= 0: continue
        fx, fy, fr = cx + x * p0, cy + y * p0, r * pi_ * p0
        col = RED if highlight != i else mix(RED, OCHRE, .35)
        paper_shape(ctx, ellipse_pts(fx, fy, fr, fr, 44), col, a, seed + 10 + i, shadow=.18, grain=.9, shade=.15)
        shown.append((fx, fy, fr))
        if fibers_t is not None:
            pf = ph(t, fibers_t + i * .05, .6)
            if pf > 0:
                for j, (u, v, rr) in enumerate(packed_circles(1.0, .15, 77 + i % 4, 40)):
                    set_c(ctx, RED_D, .55 * a * pf); ctx.arc(fx + u * fr * .92, fy + v * fr * .92, rr * fr * .92 * pf, 0, 2 * math.pi); ctx.stroke()
                    set_c(ctx, BLUSH, .35 * a * pf); ctx.arc(fx + u * fr * .92, fy + v * fr * .92, rr * fr * .8 * pf, 0, 2 * math.pi); ctx.fill()
        ink(ctx, ellipse_pts(fx, fy, fr, fr, 40), 1.6, CREAM, .8 * a, seed=seed + 40 + i, closed=True, sketch=False)
    ink(ctx, ellipse_pts(cx, cy, Rr, Rr, 90), 2.0, RED_D, .7 * a, seed=seed + 2, closed=True)
    return shown

def fiber_tube(ctx, x0, x1, cy, h, a=1.0, seed=0, col=RED, nuclei=True, stri=True, prog=1.0, cut=False, stri_sp=10):
    """a long muscle fiber (cylinder)"""
    xe = lerp(x0, x1, prog)
    if xe - x0 < 10: return
    r = h / 2
    pts = [(x0 + r * .4, cy - r)] + [(xe, cy - r)] + [(xe + r * .35 * math.cos(q), cy + r * math.sin(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 12)][1:-1] + [(xe, cy + r), (x0 + r * .4, cy + r)] \
        + [(x0 + r * .4 - r * .35 * math.cos(q), cy - r * math.sin(q)) for q in np.linspace(-math.pi / 2, math.pi / 2, 12)][1:-1]
    paper_shape(ctx, pts, col, a, seed, shadow=.2, grain=1.0, shade=.3, shade_dir=(0, 1))
    ctx.save(); path(ctx, pts, True); ctx.clip()
    if stri:
        x = x0 + 6
        k = 0
        while x < xe - 4:
            ink(ctx, [(x, cy - r), (x + 2, cy + r)], 1.0 if k % 2 else 1.6, RED_D, (.22 if k % 2 else .35) * a, seed=seed + k, sketch=False, amp=.5)
            x += stri_sp; k += 1
    # highlight band
    set_c(ctx, CREAM, .18 * a); ctx.rectangle(x0, cy - r * .7, xe - x0, r * .25); ctx.fill()
    ctx.restore()
    nl = []
    if nuclei:
        rng = np.random.default_rng(seed)
        for i in range(int((xe - x0) / 150)):
            nx = x0 + 60 + i * 150 + rng.random() * 60; ny = cy + (r * .72 if i % 2 else -r * .72)
            if nx < xe - 30:
                paper_shape(ctx, ellipse_pts(nx, ny, 17, 6.5, 16), SLATE, a, seed + 100 + i, shadow=.08, grain=.4, amp=.4, outline=INK, ow=1.0)
                nl.append((nx, ny))
    ink(ctx, pts, 1.5, RED_D, .65 * a, seed=seed + 3, closed=True)
    return nl

def myofibril(ctx, x0, x1, cy, h, a=1.0, seed=0, period=120, prog=1.0, contract=0.0, hl=None, t=0):
    """striated myofibril: repeating Z / I / A / H bands"""
    xe = lerp(x0, x1, prog)
    if xe - x0 < 5: return
    per = period * (1 - .2 * contract)
    rr = rrect_pts(x0, cy - h / 2, xe - x0, h, h * .45)
    paper_shape(ctx, rr, mix(BLUSH, CREAM, .2), a, seed, shadow=.14, grain=.8, amp=.8)
    ctx.save(); path(ctx, rr, True); ctx.clip()
    x = x0 - per * .5 + (per * .5)
    k = 0
    while x < xe + per:
        # A band (dark), centred in each period
        aw = per * .5 * (1 / (1 - .2 * contract)) * (1 - .2 * contract) if False else period * .48
        ax = x + per / 2 - aw / 2
        set_c(ctx, RED, .85 * a); ctx.rectangle(ax, cy - h / 2, aw, h); ctx.fill()
        hz = max(0, period * .16 - period * .2 * contract)
        set_c(ctx, mix(RED, BLUSH, .45), .9 * a); ctx.rectangle(x + per / 2 - hz / 2, cy - h / 2, hz, h); ctx.fill()
        # Z line
        set_c(ctx, INK, .75 * a); ctx.rectangle(x - 1.2, cy - h / 2, 2.4, h); ctx.fill()
        if hl is not None and k == hl:
            glow(ctx, x + per / 2, cy, per * .9, OCHRE_L, .6 * a)
        x += per; k += 1
    ctx.restore()
    ink(ctx, rr, 1.3, RED_D, .6 * a, seed=seed + 1, closed=True)

def actin(ctx, xa, xb, y, a=1.0, seed=0, bead=5.2, sites=0.0, blocked=1.0):
    """thin filament: two twisted bead strands (+ tropomyosin line)"""
    if a <= 0: return
    n = int(abs(xb - xa) / (bead * 1.7)) + 1
    sgn = 1 if xb > xa else -1
    for strand in (0, 1):
        for i in range(n):
            x = xa + sgn * i * bead * 1.7
            ph_ = i * .38 + strand * math.pi
            yy = y + math.sin(ph_) * bead * .9
            front = math.cos(ph_) > 0
            c = OCHRE if front else mix(OCHRE, RED_D, .35)
            ctx.arc(x, yy, bead * (1.0 if front else .85), 0, 2 * math.pi)
            set_c(ctx, c, a); ctx.fill_preserve(); set_c(ctx, INK, .35 * a); ctx.set_line_width(.8); ctx.stroke()
            if sites > 0 and strand == 0 and i % 6 == 3:
                glow(ctx, x, y - bead * 1.1, bead * 3, OCHRE_L, sites * a * .9)
                set_c(ctx, TEAL, sites * a); ctx.arc(x, y - bead * 1.3, bead * .55, 0, 2 * math.pi); ctx.fill()
    # tropomyosin cover: a thin strand that slides off the binding sites when calcium arrives
    if blocked > 0:
        off = (1 - blocked) * bead * 2.6
        pts = [(xa + sgn * (i * 8), y - bead * .9 - off + math.sin(i * .5) * 1.6) for i in range(int(abs(xb - xa) / 8))]
        if len(pts) > 1: ink(ctx, pts, 2.2, TEAL_L, a * .9, seed=seed, sketch=False, amp=.4)

def myosin(ctx, xa, xb, y, a=1.0, seed=0, head_ang=None, t=0, heads=True, thick=15, attach=None):
    """thick filament with heads; head_ang(i, side) -> angle offset (0 = cocked, 1 = power stroke done)"""
    if a <= 0: return
    paper_shape(ctx, rrect_pts(xa, y - thick / 2, xb - xa, thick, thick / 2), RED_D, a, seed, shadow=.15, grain=.7, amp=.6)
    if not heads: return
    cx = (xa + xb) / 2; bare = 36
    k = 0
    for side in (-1, 1):
        x = cx + side * bare
        i = 0
        while (side < 0 and x > xa + 8) or (side > 0 and x < xb - 8):
            up = -1 if i % 2 == 0 else 1
            st = head_ang(i, side) if head_ang else 0.0
            th = math.radians(lerp(50, 108, st))
            L = 22
            bx, by = x, y + up * thick * .45
            hx, hy = bx + side * math.cos(th) * L, by + up * math.sin(th) * L
            ink(ctx, [(bx, by), (hx, hy)], 3.2, RED_D, a, seed=seed + k, sketch=False, amp=.3)
            ctx.save(); ctx.translate(hx, hy); ctx.rotate(math.atan2(hy - by, hx - bx))
            ctx.scale(1, .62); ctx.arc(0, 0, 8.5, 0, 2 * math.pi); ctx.restore()
            set_c(ctx, mix(RED, RED_D, .3), a); ctx.fill_preserve(); set_c(ctx, INK, .5 * a); ctx.set_line_width(1); ctx.stroke()
            x += side * 26; i += 1; k += 1

def sarcomere(ctx, cx, cy, t, contract=0.0, a=1.0, scale=1.0, stroke_fn=None, sites=0.0, blocked=1.0, bands=True, rows=2, seed=0, zcol=TEAL):
    """longitudinal sarcomere diagram. contract 0..1 slides thin filaments inward."""
    half = 500 * scale * (1 - .22 * contract)
    zl, zr = cx - half, cx + half
    sp = 78 * scale
    thick_len = 290 * scale; thin_len = 360 * scale
    ytop = cy - sp * (rows + .5); ybot = cy + sp * (rows + .5)
    if bands:
        paper_shape(ctx, rect_pts(zl, ytop - 10, zr - zl, ybot - ytop + 20), mix(BLUSH, CREAM, .55), a * .9, seed + 1, shadow=.15, grain=.7, amp=.8)
        paper_shape(ctx, rect_pts(cx - thick_len, ytop - 10, thick_len * 2, ybot - ytop + 20), mix(BLUSH, RED_L, .45), a * .8, seed + 2, shadow=0, grain=.7, amp=.8)
    # thin filaments
    for r in range(-rows, rows + 1):
        y = cy + r * sp
        actin(ctx, zl, zl + thin_len, y, a, seed + 10 + r, bead=5.2 * scale, sites=sites, blocked=blocked)
        actin(ctx, zr, zr - thin_len, y, a, seed + 20 + r, bead=5.2 * scale, sites=sites, blocked=blocked)
    # thick filaments
    for r in range(-rows, rows):
        y = cy + (r + .5) * sp
        myosin(ctx, cx - thick_len, cx + thick_len, y, a, seed + 40 + r, head_ang=(lambda i, s, r=r: stroke_fn(i, s, r)) if stroke_fn else None, t=t)
    # M line
    ink(ctx, [(cx, ytop + 20), (cx, ybot - 20)], 1.6, INK_SOFT, .5 * a, seed=seed + 5, dash=[6, 6])
    # Z discs
    for zx in (zl, zr):
        ink(ctx, zigzag(zx, ytop - 18, ybot + 18, 9 * scale, 14), 4.2 * scale, zcol, a, seed=seed + int(zx), sketch=True)
    return zl, zr, ytop, ybot
