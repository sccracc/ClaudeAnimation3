from .core import *
from .scene import *
from .assets import *
from .figure import Figure

def dial(ctx, cx, cy, r, val, t, a=1.0, seed=0, zone=None, lab="load"):
    """hand-drawn gauge, val 0..1"""
    paper_shape(ctx, ellipse_pts(cx, cy, r + 26, r + 26, 60, 0, math.pi, 2 * math.pi) + [(cx + r + 26, cy + 30), (cx - r - 26, cy + 30)], CREAM, a, seed, shadow=.18)
    arc = ellipse_pts(cx, cy, r, r, 50, 0, math.pi, 2 * math.pi)
    ink(ctx, arc, 3, INK, a, seed=seed + 1)
    if zone:
        z0, z1, zc = zone
        za = ellipse_pts(cx, cy, r - 14, r - 14, 30, 0, math.pi + math.pi * z0, math.pi + math.pi * z1)
        ink(ctx, za, 14, zc, a * .85, seed=seed + 2, sketch=False)
    for k in range(11):
        ang = math.pi + math.pi * k / 10
        ink(ctx, [(cx + math.cos(ang) * r * .86, cy + math.sin(ang) * r * .86), (cx + math.cos(ang) * r, cy + math.sin(ang) * r)], 2 if k % 5 else 3, INK, a, sketch=False)
    ang = math.pi + math.pi * clamp(val)
    ink(ctx, [(cx, cy), (cx + math.cos(ang) * r * .8, cy + math.sin(ang) * r * .8)], 5, RED, a, seed=seed + 3, sketch=False)
    dots(ctx, [(cx, cy)], 10, INK, a)
    text(ctx, lab, cx, cy + 70, 'hand', 40, INK, a, 'center')

class Recruitment(Scene):
    sid = "s04_recruitment"
    extra = 0.5

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        cordx = 250
        ink(ctx, [(cordx, -20), (cordx + 10, 540), (cordx, 1100)], 34, mix(PAPER_D, SLATE_L, .5), ph(t, 0, .8), prog=ph(t, 0, 1.0, ease), seed=900, sketch=False)
        text(ctx, "spinal cord", cordx - 20, 1040, 'hand', 32, INK_SOFT, ph(t, .5, .6), 'center')
        # fibers: 12 fibers stacked; unit membership
        units = [  # (name, cell y, cell r, color, fiber indices, axon width)
            ("small", 300, 16, TEAL, [2, 9], 3),
            ("medium", 540, 24, OCHRE, [0, 4, 7, 11], 5),
            ("large", 790, 34, RED_D, [1, 3, 5, 6, 8, 10], 8)]
        fy = [230 + i * 58 for i in range(12)]
        fh = [34, 50, 30, 50, 40, 50, 50, 40, 50, 30, 50, 40]
        tl = c("light") - .2; tm = c("heavier") - .3; tL = c("larger") - .4
        rec = [ph(t, tl, .8), ph(t, tm + .5, .8), ph(t, tL + .3, .8)]
        # one-unit highlight window
        one = win(t, c("one") - .3, c("light") - .4, .4, .4)
        ent = ph(t, .2, 1.2, ease)
        sparse = win(t, .6, c("muscles") - .1, .4, .5)
        if sparse > 0:
            text(ctx, "not every fiber fires at once", 1430, 150, 'serif_i', 48, INK, sparse, 'center', reveal=ph(t, .7, .9))
        fa = {}
        for ui, (nm, cy_, cr, col, fis, aw) in enumerate(units):
            for fi in fis: fa[fi] = (ui, col)
        for i in range(12):
            ui, col = fa[i]
            base = mix(RED, PAPER, .55)
            on = max(rec[ui], sparse * max(0.0, math.sin(t * 2.6 + i * 2.3)) ** 6)
            fc = mix(base, RED, on)
            fiber_tube(ctx, 1020, 1840, fy[i], fh[i], ent * (1 - .6 * one * (ui != 1)), seed=910 + i, col=fc, nuclei=False, stri_sp=12)
            if on > 0:
                glow(ctx, 1430, fy[i], 200, OCHRE_L, on * (.25 + .15 * math.sin(t * 9 + i)))
        # neurons and axons
        for ui, (nm, cy_, cr, col, fis, aw) in enumerate(units):
            p = ph(t, c("motor") - .5 + ui * .25, 1.0, ease)
            dim = 1 - .6 * one * (ui != 1)
            cx_ = cordx + 20
            trunk = catmull([(cx_, cy_), (520, cy_ + 10), (760, cy_ - 10), (900, 540 + (cy_ - 540) * .6)], 10)
            ink(ctx, trunk, aw, col, dim, prog=p, seed=920 + ui)
            end = trunk[-1]
            for j, fi in enumerate(fis):
                br = qbez(end, (960, fy[fi] + (end[1] - fy[fi]) * .2), (1060, fy[fi]), 10)
                ink(ctx, br, max(1.6, aw * .5), col, dim, prog=ph(t, c("motor") + .3 + ui * .25, .7, ease), seed=930 + ui * 10 + j)
                dots(ctx, [(1060, fy[fi])], 5 * ph(t, c("motor") + .8, .3), col, dim)
            blob(ctx, cx_, cy_, cr * p, mix(col, CREAM, .35), dim, seed=940 + ui, outline=col, ow=2)
            # firing pulses
            if rec[ui] > 0:
                rate = 1.4
                for k in range(3):
                    q = ((t - (tl, tm + .5, tL + .3)[ui]) * rate / 1.2 + k / 3) % 1.0
                    x, y = point_at(trunk, q)
                    glow(ctx, x, y, 34 + aw * 3, OCHRE_L, rec[ui]); dots(ctx, [(x, y)], 4 + aw * .4, CREAM, rec[ui])
            text(ctx, "%s unit" % nm, cx_ + 60, cy_ - cr - 14, 'hand', 36, col, ph(t, c("motor") + .2 + ui * .3, .6))
        # "one motor unit" bracket
        if one > 0:
            circle_mark(ctx, 290, 540, 70, 60, t, c("one") - .1, OCHRE, 3, one, seed=950)
            text(ctx, "one motor unit = one nerve + the fibers it controls", 1060, 176, 'serif_i', 46, INK, one, 'center', reveal=one)
        # load dial
        val = keys(t, [(0, .05), (tl, .05), (tl + .8, .22), (tm, .22), (tm + 1.0, .6), (tL, .6), (tL + 1.0, .92)])
        da = ph(t, tl - .6, .6) * (1 - ph(t, c("these") - .4, .5))
        if da > 0:
            dial(ctx, 620, 1000, 110, val, t, da, seed=960, zone=(.75, 1.0, RED_L), lab="")
            text(ctx, "load / effort", 620, 1070, 'hand', 34, INK, da, 'center')
        # growth potential note
        g = ph(t, c("greatest") - .3, .8)
        if g > 0:
            caption_card(ctx, "the biggest units: most potential to grow", 1420, 140, t, c("greatest") - .3, size=42, seed=970, c=RED_D)
        ch = ph(t, c("challenging") - .8, .8)
        if ch > 0:
            caption_card(ctx, "only fully recruited when effort is high", 620, 990, t, c("challenging") - .8, size=38, seed=971)
        chapter_tag(ctx, t, 3, "Lifting heavy")


class Fatigue(Scene):
    sid = "s05_fatigue"
    extra = 0.6

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        t2 = c("during") - .3; t3 = c("lactate") + .1; t4 = c("as") - .9
        a1 = 1 - ph(t, t2 - .3, .6); a2 = win(t, t2, t3, .6, .6); a3 = win(t, t3, t4 + .4, .6, .6); a4 = ph(t, t4 - .2, .6)
        if a1 > 0: self.energy(ctx, t, a1)
        if a2 > 0: self.acid(ctx, t, a2)
        if a3 > 0: self.lactate(ctx, t, a3)
        if a4 > 0: self.fatigue(ctx, t, a4)
        chapter_tag(ctx, t, 4, "The burn, and fatigue")

    def tank(self, ctx, x, y, w, h, level, col, a, seed, lab, sub=None):
        paper_shape(ctx, rrect_pts(x, y, w, h, 18), CREAM, a, seed, shadow=.2, outline=INK, ow=2.2)
        lv = clamp(level)
        if lv > 0.01:
            wob = [(x + 8 + i * (w - 16) / 20, y + h - 8 - (h - 16) * lv + math.sin(i * .8 + self._t * 3) * 3) for i in range(21)]
            poly = wob + [(x + w - 8, y + h - 8), (x + 8, y + h - 8)]
            paper_shape(ctx, poly, col, a, seed + 1, shadow=0, amp=.8)
        text(ctx, lab, x + w / 2, y - 22, 'title', 48, INK, a, 'center')
        if sub: text(ctx, sub, x + w / 2, y + h + 50, 'hand', 34, INK_SOFT, a, 'center')

    def energy(self, ctx, t, a):
        c = self.cue; self._t = t
        # ATP cup drained by contractions, refilled by two pipes
        drain = ph(t, c("stores") - .3, 1.8, ein)
        refill1 = ph(t, c("phosphocreatine") - .3, 1.0) ; refill2 = ph(t, c("glucose") - .3, 1.0)
        lvl = 1 - drain * .85 + .35 * refill1 + .3 * refill2
        lvl = min(lvl, .9) - .06 * math.sin(t * 5) * (drain > .9)
        ax, ay = 820, 380
        self.tank(ctx, ax, ay, 280, 360, lvl * ph(t, 0, .8), OCHRE, a, 1000, "ATP", "the muscle's ready fuel")
        # muscle using it (arrow out to a pulling fiber)
        fiber_tube(ctx, 1300, 1840, 560, 120, a, seed=1010, nuclei=False, stri_sp=10)
        arrow(ctx, [(1110, 560), (1290, 560)], 3.2, INK, a, prog=ph(t, c("pulling") - .2, .6), seed=1011)
        for k in range(4):
            q = (t * .9 + k / 4) % 1
            x, y = lerp(1115, 1285, q), 560
            blob(ctx, x, y, 10, OCHRE_L, a * ph(t, c("burns"), .5), seed=1012 + k, shadow=.1)
        # "a few seconds" note
        sn = ph(t, c("few") - .2, .7)
        if sn > 0:
            clock_icon(ctx, 960, 900, 46, (t - c("few")) * .8, a * sn, seed=1020)
            text(ctx, "stored: only a few seconds' worth", 1030, 912, 'hand', 40, RED, a * sn, 'left', reveal=sn)
        # refill sources
        for i, (nm, y, col, tt) in enumerate([("phosphocreatine", 330, SLATE_L, c("phosphocreatine")), ("glucose", 640, SAGE, c("glucose"))]):
            p = ph(t, tt - .5, .7)
            if p <= 0: continue
            self.tank(ctx, 230, y, 260, 200, .85 - .3 * ph(t, tt, 3), col, a * p, 1030 + i * 5, "", None)
            text(ctx, nm, 360, y - 20, 'serif_i', 44, INK, a * p, 'center', reveal=p)
            text(ctx, "fast, brief" if i == 0 else "slower, lasts longer", 360, y + 245, 'hand', 32, INK_SOFT, a * p, 'center')
            pipe = catmull([(490, y + 100), (650, y + 100), (700, ay + 180 + (i - .5) * 90), (820, ay + 180 + (i - .5) * 90)], 8)
            ink(ctx, pipe, 10, col, a * p, prog=p, seed=1040 + i, sketch=False)
            ink(ctx, pipe, 1.6, INK_SOFT, a * p * .6, prog=p, seed=1042 + i)
            for k in range(3):
                q = (t * .7 + k / 3) % 1
                x, y2 = point_at(pipe, q); blob(ctx, x, y2, 8, OCHRE, a * p, seed=1050 + k + i * 5, shadow=.1)
        text(ctx, "rebuilt constantly", 960, 300, 'hand', 40, INK, a * ph(t, c("constantly") - .1, .6), 'center', reveal=ph(t, c("constantly") - .1, .8))

    def acid(self, ctx, t, a):
        c = self.cue
        cx, cy, R = 760, 560, 330
        paper_shape(ctx, ellipse_pts(cx, cy, R + 16, R + 16, 90), CREAM, a, 1100, shadow=.22)
        paper_shape(ctx, ellipse_pts(cx, cy, R, R, 90), mix(RED, BLUSH, .35), a, 1101, shadow=0, grain=1.0)
        for j, (u, v, rr) in enumerate(packed_circles(1.0, .1, 9, 80)):
            ink(ctx, ellipse_pts(cx + u * R * .9, cy + v * R * .9, rr * R * .85, rr * R * .85, 14), 1.2, RED_D, a * .5, seed=1110 + j, closed=True, sketch=False)
        text(ctx, "inside a working fiber", cx, cy - R - 40, 'serif_i', 44, INK, a, 'center')
        n = int(70 * ph(t, c("hydrogen") - .8, 3.0))
        rng = np.random.default_rng(4)
        for k in range(n):
            ang = rng.random() * 6.28; d = math.sqrt(rng.random()) * R * .85
            x = cx + math.cos(ang + t * .15 * (rng.random() - .5)) * d; y = cy + math.sin(ang + t * .15 * (rng.random() - .5)) * d
            blob(ctx, x, y, 13, hexc('E0664B'), a, seed=1200 + k, shadow=.12, grain=.3)
            text(ctx, "H⁺", x, y + 6, 'sans_b', 15, CREAM, a, 'center')
        burn = ph(t, c("thats") - .2, .8)
        if burn > 0:
            glow(ctx, cx, cy, R * 1.25, hexc('E8743B'), a * burn * (.55 + .2 * math.sin(t * 5)))
        label(ctx, "hydrogen ions", 1250, 330, cx + 200, cy - 150, t, c("hydrogen") - .2, font='serif_i', size=48, seed=21, a=a)
        # pH strip
        pa = ph(t, c("acidic") - .8, .6)
        if pa > 0:
            x0, y0 = 1250, 480
            cols = [hexc('D9534A'), hexc('E07B4E'), hexc('E8A45A'), hexc('D8C063'), hexc('9DB46A'), hexc('6E9E7A')]
            for i, col in enumerate(cols):
                paper_shape(ctx, rect_pts(x0 + i * 90, y0, 90, 60), col, a * pa, 1300 + i, shadow=.1, amp=.6)
            for i, lab in enumerate(["6.4", "", "6.8", "", "7.1", ""]):
                if lab: text(ctx, lab, x0 + i * 90 + 45, y0 + 100, 'sans', 28, INK, a * pa, 'center')
            text(ctx, "muscle pH", x0 + 270, y0 - 24, 'hand', 36, INK, a * pa, 'center')
            ph_v = keys(t, [(c("acidic") - .6, 7.05), (c("thats"), 6.55)])
            px = x0 + (ph_v - 6.4) / (7.2 - 6.4) * 540
            ink(ctx, [(px, y0 - 10), (px, y0 + 70)], 5, INK, a * pa, sketch=False)
            ink(ctx, [(px - 12, y0 - 24), (px, y0 - 8), (px + 12, y0 - 24)], 4, INK, a * pa, sketch=False)
            text(ctx, "more acidic", x0 + 90, y0 + 150, 'hand', 40, RED, a * pa, 'center', reveal=ph(t, c("acidic"), .6))
        if burn > 0:
            text(ctx, "= a big part of the burn", 1520, 760, 'title_i', 56, RED_D, a * burn, 'center', reveal=burn)

    def lactate(self, ctx, t, a):
        c = self.cue
        p = ph(t, c("lactate") - .3, .7, eback)
        p = max(p, 0.001)
        ctx.save(); ctx.translate(560, 540); ctx.rotate(-.04); ctx.scale(p, p); ctx.translate(-560, -540)
        paper_shape(ctx, rect_pts(300, 400, 520, 260), CREAM, a, 1400, shadow=.25)
        text(ctx, "Lactate", 560, 520, 'title', 86, INK, a, 'center')
        text(ctx, "“the cause of the burn”", 560, 600, 'serif_i', 40, INK_SOFT, a, 'center')
        ctx.restore()
        x = ph(t, c("blame") - .1, .5)
        ink(ctx, [(330, 620), (800, 420)], 6, RED, a * x, prog=x, seed=1401)
        text(ctx, "not quite", 560, 730, 'hand', 44, RED, a * x, 'center', reveal=x)
        # recycling loop
        q = ph(t, c("actually") - .3, 1.2, ease)
        if q > 0:
            cx, cy, r = 1350, 540, 210
            pts = ellipse_pts(cx, cy, r, r, 80, 0, -math.pi / 2 + .25, -math.pi / 2 + 2 * math.pi - .25)
            arrow(ctx, pts, 4, TEAL, a, prog=q, seed=1410, head=22)
            text(ctx, "lactate", cx, cy - r - 30, 'hand', 40, INK, a * q, 'center')
            # heart
            hx, hy = cx + r + 10, cy + 10
            heart = [(hx, hy + 30)] + [(hx + 30 * math.sin(tt) ** 3 * 1.1, hy - 26 * math.cos(tt) + 10 * math.cos(2 * tt) + 5 * math.cos(3 * tt) + math.cos(4 * tt)) for tt in np.linspace(0, 2 * math.pi, 40)]
            paper_shape(ctx, heart, RED, a * q, 1420, shadow=.15)
            text(ctx, "heart, liver,", hx + 70, hy - 10, 'hand', 34, INK_SOFT, a * q)
            text(ctx, "other muscles", hx + 70, hy + 30, 'hand', 34, INK_SOFT, a * q)
            text(ctx, "fuel", cx, cy + r + 60, 'hand', 44, INK, a * q, 'center')
            text(ctx, "recycled", cx, cy + 16, "title_i", 56, TEAL, a * ph(t, c("fuel") - .2, .7), "center", reveal=ph(t, c("fuel") - .2, .8))

    def fatigue(self, ctx, t, a):
        c = self.cue
        x0, y0 = 300, 820
        axes(ctx, x0, y0, 900, 520, t, c("as") - 1.1, xl="rep number", yl="force per rep", a=a, seed=1500)
        n = 10
        for i in range(n):
            p = ph(t, c("byproducts", 2) + i * .28, .5, eback)
            if p <= 0: continue
            hgt = 440 * (1 - .058 * i - .002 * i * i) * p
            col = mix(RED, RED_L, i / n)
            paper_shape(ctx, rect_pts(x0 + 40 + i * 84, y0 - hgt, 60, hgt), col, a, 1510 + i, shadow=.15)
            text(ctx, str(i + 1), x0 + 70 + i * 84, y0 + 40, 'sans', 26, INK_SOFT, a * p, 'center')
        hd = ph(t, c("harder") - .3, .7)
        if hd > 0:
            arrow(ctx, catmull([(x0 + 80, y0 - 480), (x0 + 450, y0 - 400), (x0 + 850, y0 - 200)], 10), 3.2, INK, a * hd, prog=hd, seed=1530)
            text(ctx, "each rep gets harder", x0 + 560, y0 - 470, 'hand', 44, INK, a * hd, 'left', reveal=hd)
        f = ph(t, c("fatigue") - .3, .9, ease)
        if f > 0:
            text(ctx, "Fatigue", 1540, 480, 'title', 110, INK, a * f, 'center', reveal=f, rise=10)
            underline(ctx, 1370, 1710, 505, t, c("fatigue"), RED, 5, a, seed=1540)
            text(ctx, "a temporary,", 1540, 590, 'serif_i', 50, INK_SOFT, a * ph(t, c("temporary") - .2, .6), 'center', reveal=ph(t, c("temporary") - .2, .8))
            text(ctx, "protective slowdown", 1540, 650, 'serif_i', 50, INK_SOFT, a * ph(t, c("protective") - .2, .6), 'center', reveal=ph(t, c("protective") - .2, .8))


class Damage(Scene):
    sid = "s06_damage"
    extra = 0.5

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        z1 = c("microscopic") - .6
        t2 = c("soreness") - .6; t3 = c("but") - .4
        a12 = 1 - ph(t, t2 - .3, .6)
        if a12 > 0:
            ctx.push_group()
            background(ctx, t)
            zoom_through(ctx, t, z1, 1.3, (735, 570), lambda cx: self.arm(cx, t), lambda cx: self.micro(cx, t), zmax=6, bg_t=t)
            ctx.pop_group_to_source(); ctx.paint_with_alpha(a12)
        a2 = win(t, t2, t3, .6, .6)
        if a2 > 0: self.sore(ctx, t, a2)
        a3 = ph(t, t3, .6)
        if a3 > 0: self.tension(ctx, t, a3)
        chapter_tag(ctx, t, 5, "Micro-damage")

    def sfx(self):
        return [(self.cue("microscopic") - .6, 'zoom')]

    def arm(self, ctx, t):
        c = self.cue
        f = Figure(700, 470, .86)
        th = keys(t, [(0, 2.0), (c("lowering") - .2, 2.0), (c("microscopic") - .4, .6)], fn=lambda x: x)
        f.draw(ctx, t, theta=th, skin=1.0, peel=(f.P((40, 120))[0], f.P((40, 120))[1], 150), glow_biceps=.4)
        la = ph(t, c("lowering") - .3, .6)
        if la > 0:
            text(ctx, "the lowering phase", 1130, 360, 'serif_i', 60, INK, la, 'left', reveal=la)
            text(ctx, "muscle lengthens while under load", 1130, 430, 'hand', 42, INK_SOFT, la, 'left', reveal=ph(t, c("lowering") + .2, .8))
            arrow(ctx, [(1000, 300), (1000, 620)], 3.4, RED, la, prog=la, seed=1601)

    def micro(self, ctx, t):
        c = self.cue
        # myofibrils with disrupted sarcomeres
        for i, y in enumerate([380, 470, 560, 650, 740]):
            myofibril(ctx, 120, 1800, y, 56, 1, seed=1610 + i, period=150)
        # damage: wavy, misaligned Z-lines + small tears
        rng = np.random.default_rng(5)
        dm = ph(t, c("damage") - .3, 1.0)
        for k in range(7):
            x = 700 + rng.random() * 700; y = 400 + rng.random() * 320
            tear = [(x + dx, y + math.sin(dx * .3 + k) * 10 + (rng.random() - .5) * 8) for dx in range(-40, 41, 8)]
            ink(ctx, tear, 10 * dm, CREAM, dm, seed=1650 + k, sketch=False)
            ink(ctx, [(p_[0] + 3, p_[1] + 4) for p_ in tear], 1.4, INK, dm * .6, seed=1660 + k)
        if dm > 0:
            ctx.save(); ctx.rectangle(900, 330, 400, 460); ctx.clip()
            for j in range(3):
                zx = 1000 + j * 150
                ink(ctx, [(zx + math.sin(yy * .05 + j) * 22 * dm, yy) for yy in range(340, 780, 12)], 3, INK, dm * .8, seed=1670 + j)
            ctx.restore()
            circle_mark(ctx, 1100, 560, 330, 260, t, c("damage"), RED, 3.6, 1, seed=1680)
        text(ctx, "microscopic damage", 960, 950, 'title_i', 66, RED_D, dm, 'center', reveal=dm)

    def sore(self, ctx, t, a):
        c = self.cue
        x0, y0, w, h = 330, 830, 1260, 520
        axes(ctx, x0, y0, w, h, t, c("soreness") - .5, xl="hours after training", a=a, seed=1700)
        for i, lab in enumerate(["0", "24", "48", "72"]):
            text(ctx, lab, x0 + i * w / 3.3, y0 + 44, 'sans', 28, INK_SOFT, a * ph(t, c("soreness"), .5), 'center')
        sore = lambda x: math.exp(-((x - .45) / .22) ** 2) * .85
        acid = lambda x: max(0, .7 * math.exp(-x / .025))
        p1 = curve(ctx, sore, x0, y0, w * 1.0, h, t, c("day") - .3, 1.6, RED, 4.5, a, seed=1710, x0=0, x1=1)
        if ph(t, c("later"), .5) > 0:
            text(ctx, "soreness", x0 + w * .45, y0 - h * .85 - 30, 'hand', 44, RED, a * ph(t, c("later"), .5), 'center')
            text(ctx, "peaks a day or two later", x0 + w * .45, y0 - h * .85 - 80, 'serif_i', 38, INK_SOFT, a * ph(t, c("later") + .2, .5), 'center')
        ra = ph(t, c("repair") - .2, .6)
        if ra > 0:
            text(ctx, "repair + inflammation", x0 + w * .72, y0 - h * .45, 'hand', 40, INK, a * ra, 'left', reveal=ra)
        la = ph(t, c("leftover") - .5, .6)
        if la > 0:
            curve(ctx, acid, x0, y0, w, h, t, c("leftover") - .5, .8, TEAL, 3.5, a, seed=1720, x0=0, x1=.25)
            text(ctx, "acid: cleared", x0 + 30, y0 - h * .74, 'hand', 34, TEAL, a * la, 'left', reveal=la)
            text(ctx, "within about an hour", x0 + 30, y0 - h * .66, 'hand', 34, TEAL, a * la, 'left', reveal=ph(t, c("leftover") - .2, .6))

    def tension(self, ctx, t, a):
        c = self.cue
        dmg = ph(t, c("but") - .3, .6)
        text(ctx, "damage", 960, 230, 'title', 80, INK_SOFT, a * dmg, 'center')
        st = ph(t, c("goal") - .3, .5)
        ink(ctx, [(800, 205), (1120, 215)], 6, RED, a * st, prog=st, seed=1801)
        text(ctx, "a side effect, not the goal", 960, 300, 'hand', 40, INK_SOFT, a * st, 'center', reveal=st)
        k = ph(t, c("key") - .3, .8, ease)
        if k > 0:
            pull = .5 + .5 * math.sin(t * 2.2)
            stretch = 20 * pull * ph(t, c("tension") - .3, .6)
            fiber_tube(ctx, 520 - stretch, 1400 + stretch, 620, 150, a * k, seed=1810, stri_sp=12 + stretch * .05)
            for sgn in (-1, 1):
                xa = 960 + sgn * (470 + stretch)
                arrow(ctx, [(xa, 620), (xa + sgn * 170, 620)], 6, RED, a * k, prog=ph(t, c("tension") - .4, .6), seed=1820 + sgn, head=26)
            text(ctx, "mechanical tension", 960, 860, 'title', 92, RED_D, a * ph(t, c("mechanical") - .2, .8), 'center', reveal=ph(t, c("mechanical") - .2, 1.0), rise=8)
            text(ctx, "the key signal for growth", 960, 470, 'serif_i', 52, INK, a * k, 'center', reveal=k)
            text(ctx, "fibers producing high force", 960, 940, 'hand', 44, INK_SOFT, a * ph(t, c("producing") - .3, .6), 'center', reveal=ph(t, c("producing") - .3, .8))
            if ph(t, c("tension") - .3, .5) > 0:
                glow(ctx, 960, 620, 520, OCHRE_L, a * .35 * pull)
