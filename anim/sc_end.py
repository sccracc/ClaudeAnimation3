from .core import *
from .scene import *
from .assets import *
from .figure import Figure

class Repair(Scene):
    sid = "s07_repair"
    extra = 0.8

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        t2 = c("for") - .4; t3 = c("nearby") - .4; t4 = c("when") - .4
        a1 = 1 - ph(t, t2 - .2, .5); a2 = win(t, t2, t3, .5, .5); a3 = win(t, t3, t4, .5, .5); a4 = ph(t, t4, .5)
        if a1 > 0: self.signal(ctx, t, a1)
        if a2 > 0: self.mps(ctx, t, a2)
        if a3 > 0: self.satellite(ctx, t, a3)
        if a4 > 0: self.hyper(ctx, t, a4)
        chapter_tag(ctx, t, 6, "Recovery and rebuilding")

    def signal(self, ctx, t, a):
        c = self.cue
        # a large fiber seen from inside; membrane on top with sensors
        paper_shape(ctx, rect_pts(-40, 300, 2000, 520), mix(RED, BLUSH, .3), a, 2000, shadow=.2, grain=1.0)
        ink(ctx, [(-40, 300), (1960, 300)], 5, RED_D, a, seed=2001)
        pull = .5 + .5 * math.sin(t * 2.4)
        for sgn in (-1, 1):
            arrow(ctx, [(960 + sgn * 500, 220), (960 + sgn * (680 + 30 * pull), 220)], 5, RED, a * ph(t, 0, .6), seed=2002 + sgn, head=24)
        text(ctx, "tension", 960, 235, 'hand', 48, RED, a * ph(t, 0, .6), 'center')
        sens = [300, 620, 940, 1260, 1580]
        for i, x in enumerate(sens):
            blob(ctx, x, 300, 22, TEAL_L, a, seed=2010 + i, outline=TEAL, ow=1.6, squash=1.4)
            s_on = ph(t, c("sense") - .2 + i * .1, .4)
            if s_on > 0: glow(ctx, x, 300, 70, TEAL_L, a * s_on * (.6 + .3 * math.sin(t * 6 + i)))
        label(ctx, "sensors in the fiber", 180, 180, 300, 285, t, c("sense") - .1, size=38, seed=31, a=a)
        # cascade toward the mTOR switch
        sx, sy = 960, 640
        for i, x in enumerate(sens):
            p = ph(t, c("switch") - .4 + i * .08, 1.2, ease)
            path_ = qbez((x, 320), ((x + sx) / 2, 420), (sx, sy - 60), 16)
            ink(ctx, path_, 2.2, TEAL, a * .7 * min(1, p * 2), prog=p, seed=2020 + i, dash=[8, 6])
            for k in range(2):
                q = (t * .6 + k * .5 + i * .13) % 1
                if p >= 1:
                    x2, y2 = point_at(path_, q); blob(ctx, x2, y2, 7, OCHRE, a, seed=2030 + i * 3 + k, shadow=.1)
        on = ph(t, c("em-tor") - .2, .6, eback)
        ba = a * ph(t, c("switch") - .3, .5)
        paper_shape(ctx, rrect_pts(sx - 170, sy - 40, 340, 150, 14), CREAM, ba, 2040, shadow=.22, outline=INK, ow=2)
        if ba > 0:
            px, py = sx, sy + 80
            # contact studs + pivot
            for sgn in (-1, 1):
                blob(ctx, sx + sgn * 105, sy - 5, 13, INK_SOFT if sgn < 0 else mix(SAGE, INK_SOFT, .3), ba, seed=2043 + sgn, shadow=.12)
            ang = math.radians(lerp(-52, 52, clamp(on)))
            lx, ly = px + math.sin(ang) * 118, py - math.cos(ang) * 118
            ink(ctx, [(px, py), (lx, ly)], 9, INK_SOFT, ba, seed=2045, sketch=False, amp=.6)
            blob(ctx, lx, ly, 17, RED if on < .5 else SAGE, ba, seed=2046, outline=INK, ow=1.6)
            blob(ctx, px, py, 12, OCHRE, ba, seed=2047, outline=INK, ow=1.4)
            text(ctx, "off", sx - 150, sy - 50, 'hand', 32, INK_SOFT, ba * .8, 'center')
            text(ctx, "on", sx + 150, sy - 50, 'hand', 32, hexc('4E6F3A'), ba, 'center')
            text(ctx, "mTOR", sx, sy - 70, 'title', 64, INK, a * ph(t, c("em-tor") - .3, .5), 'center', reveal=ph(t, c("em-tor") - .3, .6))
            if on > .5:
                for r in (1, 2, 3):
                    q = ((t * .8) + r / 3) % 1
                    ink(ctx, ellipse_pts(sx, sy + 15, 150 + q * 260, 60 + q * 120, 60), 2, SAGE, a * (1 - q) * .7, seed=2050 + r, closed=True, sketch=False)
                text(ctx, "growth signals switched on", sx, sy + 200, 'hand', 44, hexc('4E6F3A'), a, 'center', reveal=ph(t, c("em-tor") + .2, .8))

    def mps(self, ctx, t, a):
        c = self.cue
        x0, y0, w, h = 260, 800, 1000, 460
        axes(ctx, x0, y0, w, h, t, c("for") - .3, xl="hours after training", yl="protein building", a=a, seed=2100)
        base = .3
        ink(ctx, [(x0, y0 - h * base), (x0 + w, y0 - h * base)], 2, INK_SOFT, a * ph(t, c("for"), .5), seed=2101, dash=[9, 8])
        text(ctx, "normal", x0 + w - 10, y0 - h * base + 36, 'hand', 32, INK_SOFT, a * ph(t, c("for"), .5), 'right')
        f = lambda x: base + .62 * (x / .12) * math.exp(1 - x / .12) * (1 if x < .9 else 1) if x > 0 else base
        curve(ctx, lambda x: base + .6 * (min(x, .95) / .14) * math.exp(1 - min(x, .95) / .14) * (1 - x * .25), x0, y0, w, h, t, c("day") - .2, 1.8, SAGE, 5, a, seed=2110, x0=0, x1=1)
        for i, lab in enumerate(["0", "24", "48"]):
            text(ctx, lab, x0 + i * w * .45, y0 + 44, 'sans', 28, INK_SOFT, a * ph(t, c("for"), .5), 'center')
        hi = ph(t, c("higher") - .2, .6)
        if hi > 0:
            text(ctx, "muscle protein synthesis", x0 + w * .2, y0 - h * .98, 'serif_i', 44, hexc('4E6F3A'), a * hi, 'left', reveal=hi)
            text(ctx, "stays raised for a day or two", x0 + w * .2, y0 - h * .98 + 50, 'hand', 36, INK_SOFT, a * hi, 'left', reveal=ph(t, c("higher"), .7))
        # amino acids from food
        pa = ph(t, c("using") - .3, .6)
        if pa > 0:
            plate_icon(ctx, 1500, 330, 110, a * pa, seed=2120)
            text(ctx, "protein you eat", 1500, 500, 'hand', 40, INK, a * pa, 'center')
            cols = [OCHRE, TEAL_L, RED_L, SAGE, SLATE_L, OCHRE_L]
            n = 9
            for k in range(n):
                q = ph(t, c("amino") + k * .12, 1.3, ease)
                x = lerp(1500 + (k - 4) * 12, 1330 + k * 50, q); y = lerp(420, 760 + 30 * math.sin(k * 1.3) * (1 - q * .2), q)
                if k > 0 and q >= 1:
                    xp = 1330 + (k - 1) * 50; yp = 760 + 30 * math.sin((k - 1) * 1.3) * .8
                    ink(ctx, [(xp, yp), (x, y)], 2.4, INK_SOFT, a, sketch=False)
                blob(ctx, x, y, 18, cols[k % 6], a * min(1, q * 3), seed=2130 + k, outline=INK_SOFT, ow=1.2)
            text(ctx, "amino acids, built into new protein", 1530, 880, 'hand', 40, INK, a * ph(t, c("acids") + .3, .6), 'center', reveal=ph(t, c("acids") + .3, .8))

    def satellite(self, ctx, t, a):
        c = self.cue
        fiber_tube(ctx, 150, 1770, 600, 230, a, seed=2200, nuclei=True, stri_sp=14)
        # satellite cell on the surface, fuses in and its nucleus moves inside
        fu = ph(t, c("fuse") - .2, 1.6, ease)
        sx, sy = 960, lerp(450, 520, fu)
        cell_a = a * (1 - ph(t, c("fuse") + .8, .8))
        if cell_a > 0:
            blob(ctx, sx, sy, lerp(62, 40, fu), TEAL_L, cell_a, seed=2210, outline=TEAL, ow=2, squash=.7)
        nx, ny = lerp(sx, 1010, ph(t, c("donating") - .3, 1.2, ease)), lerp(sy, 640, ph(t, c("donating") - .3, 1.2, ease))
        paper_shape(ctx, ellipse_pts(nx, ny, 26, 13, 20), SLATE, a, 2211, shadow=.1, outline=INK, ow=1.2)
        g = ph(t, c("donating") + .6, .6)
        if g > 0:
            glow(ctx, nx, ny, 90, OCHRE_L, a * g * .8)
            paper_shape(ctx, ellipse_pts(1300, 700, 26, 13, 20), SLATE, a * g, 2212, shadow=.1, outline=INK, ow=1.2)
            paper_shape(ctx, ellipse_pts(640, 520, 26, 13, 20), SLATE, a * g, 2213, shadow=.1, outline=INK, ow=1.2)
        label(ctx, "satellite cell (a muscle stem cell)", 1080, 290, 990, 425, t, c("satellite") - .3, font='serif_i', size=46, seed=41, a=cell_a if fu < .5 else a * (1 - ph(t, c("fuse") + .5, .5)))
        label(ctx, "extra nuclei", 1150, 900, 1010, 655, t, c("nuclei") - .2, font='serif_i', size=48, seed=42, a=a)
        text(ctx, "more nuclei can support a bigger fiber", 1150, 960, 'hand', 36, INK_SOFT, a * ph(t, c("support") - .2, .6), 'left', reveal=ph(t, c("support") - .2, .8))

    def hyper(self, ctx, t, a):
        c = self.cue
        # balance: building vs breakdown
        ba = 1 - ph(t, c("fibers", 3) - .5, .5)
        if ba > 0:
            tilt = -.16 * ph(t, c("outpaces") - .2, 1.0, eback)
            cx, cy = 960, 520
            paper_shape(ctx, [(cx - 30, cy + 260), (cx + 30, cy + 260), (cx + 8, cy), (cx - 8, cy)], INK_SOFT, a * ba, 2300, shadow=.2)
            ctx.save(); ctx.translate(cx, cy); ctx.rotate(tilt)
            paper_shape(ctx, rect_pts(-420, -8, 840, 16), INK_SOFT, a * ba, 2301, shadow=.2)
            ctx.restore()
            for sgn, lab, col in [(-1, "building", SAGE), (1, "breakdown", RED_L)]:
                px = cx + sgn * 400 * math.cos(tilt); py = cy + sgn * 400 * math.sin(tilt)
                ink(ctx, [(px, py), (px - 70, py + 120)], 1.6, INK, a * ba, sketch=False)
                ink(ctx, [(px, py), (px + 70, py + 120)], 1.6, INK, a * ba, sketch=False)
                paper_shape(ctx, [(px - 110, py + 120), (px + 110, py + 120), (px + 80, py + 160), (px - 80, py + 160)], col, a * ba, 2310 + sgn, shadow=.2)
                text(ctx, lab, px, py + 220, 'hand', 46, INK, a * ba, 'center')
                nb = 5 if sgn < 0 else 3
                for k in range(nb):
                    blob(ctx, px - 60 + k * 30, py + 105 - (k % 2) * 16, 15, [OCHRE, TEAL_L, RED_L, SAGE, SLATE_L][k], a * ba, seed=2320 + k + sgn * 10, shadow=.1)
        # fiber cross-section before/after
        ha = ph(t, c("fibers", 3) - .3, .6)
        if ha > 0:
            grow = ph(t, c("thicker") - .4, 1.4, ease)
            for i, (cx, g, lab) in enumerate([(620, 0, "before"), (1300, grow, "after")]):
                R = 190 * (1 + .28 * g)
                paper_shape(ctx, ellipse_pts(cx, 520, R + 10, R + 10, 80), CREAM, a * ha, 2400 + i, shadow=.22)
                paper_shape(ctx, ellipse_pts(cx, 520, R, R, 80), mix(RED, BLUSH, .35), a * ha, 2402 + i, shadow=0)
                n = 30 + int(22 * g) if i == 1 else 30
                for j, (u, v, rr) in enumerate(packed_circles(1.0, .1, 21, n)):
                    new = (i == 1 and j >= 30)
                    blob(ctx, cx + u * R * .92, 520 + v * R * .92, rr * R * .9, OCHRE_L if new else RED, a * ha, seed=2410 + j, shadow=.08, grain=.5)
                text(ctx, lab, cx, 520 + 260 + 40 * i * g, 'hand', 44, INK, a * ha, 'center')
            label(ctx, "new myofibrils", 1660, 330, 1420, 440, t, c("myofibrils") - .1, size=42, seed=43, a=a)
            arrow(ctx, [(850, 520), (1060, 520)], 4, INK, a * ha, prog=ph(t, c("fibers", 3), .6), seed=2420)
            hy = ph(t, c("hypertrophy") - .3, .9, ease)
            if hy > 0:
                text(ctx, "Hypertrophy", 960, 960, 'title', 96, RED_D, a * hy, 'center', reveal=hy, rise=10)


class Neural(Scene):
    sid = "s08_neural"
    extra = 0.5

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        chapter_tag(ctx, t, 7, "Getting stronger")
        # left: axon to fiber with firing that gets faster / more units
        ent = ph(t, .1, .8)
        for i in range(3):
            y = 380 + i * 170
            on = ph(t, c("recruiting") - .3 + i * .3, .5) if i > 0 else ent
            ink(ctx, catmull([(120, y), (400, y - 30), (620, y + 20), (760, y)], 10), 5, OCHRE, ent * (.35 + .65 * on), seed=2500 + i)
            fiber_tube(ctx, 760, 900, y, 70, ent, seed=2510 + i, nuclei=False, col=mix(mix(RED, PAPER, .5), RED, on))
            rate = 1.0 + 2.5 * ph(t, c("firing") - .3, 1.0)
            if on > .5:
                for k in range(int(rate * 1.4) + 1):
                    q = (t * rate * .6 + k / (int(rate * 1.4) + 1)) % 1
                    x = lerp(120, 760, q); yy = y + (-30 * math.sin(q * math.pi) if q < .6 else 20 * math.sin((q - .6) * math.pi / .4))
                    glow(ctx, x, yy, 30, OCHRE_L, ent); dots(ctx, [(x, yy)], 5, CREAM, ent)
        text(ctx, "better coordination", 470, 250, 'serif_i', 48, INK, ph(t, c("coordination") - .3, .6), 'center', reveal=ph(t, c("coordination") - .3, .8))
        text(ctx, "more units recruited", 470, 900, 'hand', 40, INK, ph(t, c("recruiting") - .1, .6), 'center', reveal=ph(t, c("recruiting") - .1, .8))
        text(ctx, "firing faster", 470, 950, 'hand', 40, INK, ph(t, c("firing") - .1, .6), 'center', reveal=ph(t, c("firing") - .1, .8))
        # right: contributions over weeks
        x0, y0, w, h = 1080, 820, 700, 520
        axes(ctx, x0, y0, w, h, t, c("first") - .6, xl="weeks of training", yl="strength gained", seed=2550)
        neural = lambda x: .55 * (1 - math.exp(-x / .12))
        size = lambda x: .45 * max(0, (x - .15) / .85) ** 1.3
        curve(ctx, neural, x0, y0, w, h, t, c("first") - .2, 1.6, OCHRE, 5, 1, seed=2560, x0=0, x1=1)
        curve(ctx, lambda x: neural(x) + size(x), x0, y0, w, h, t, c("size") - .3, 1.6, RED, 5, 1, seed=2561, x0=0, x1=1)
        text(ctx, "nervous system", x0 + w * .55, y0 - h * .45, 'hand', 40, hexc('9A6420'), ph(t, c("first") + .6, .6), 'left')
        text(ctx, "+ muscle size", x0 + w * .6, y0 - h * 1.02, 'hand', 40, RED, ph(t, c("size") + .2, .6), 'left')
        text(ctx, "size follows later", x0 + w * .5, 190, 'serif_i', 46, INK, ph(t, c("follows") - .2, .6), 'center', reveal=ph(t, c("follows") - .2, .8))


class Recovery(Scene):
    sid = "s09_recovery"

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        chapter_tag(ctx, t, 8, "Sleep, food and rest")
        text(ctx, "Recovery isn't optional", 960, 200, 'title', 78, INK, ph(t, c("recovery") - .3, .8), 'center', reveal=ph(t, c("recovery") - .3, 1.0), rise=8)
        cards = [("Sleep", c("sleep") - .3, "much of the rebuilding", "happens overnight"),
                 ("Protein", c("enough") - .3, "spread through the day", "(roughly 1.6 g per kg daily)"),
                 ("Rest", c("rest") - .3, "rest days let the", "rebuilding finish")]
        for i, (title, t0, l1, l2) in enumerate(cards):
            p = ph(t, t0, .8, eback)
            if p <= 0: continue
            x = 260 + i * 500; y = 300
            ctx.save(); ctx.translate(x + 200, y + 280); ctx.rotate((i - 1) * .02); ctx.scale(.85 + .15 * p, .85 + .15 * p); ctx.translate(-(x + 200), -(y + 280))
            paper_shape(ctx, rect_pts(x, y, 400, 560), CREAM, clamp(p), 2600 + i, shadow=.24)
            text(ctx, title, x + 200, y + 90, 'title', 64, INK, 1, 'center')
            if i == 0:
                moon_icon(ctx, x + 185, y + 250, 78, 1, seed=2610)
                zz = ph(t, t0 + .5, .5)
                for k in range(3):
                    q = ((t - t0) * .5 + k / 3) % 1
                    text(ctx, "z", x + 270 + q * 60, y + 200 - q * 90 - k * 5, 'hand_b', 30 + k * 6, SLATE, zz * (1 - q), 'center')
            elif i == 1:
                plate_icon(ctx, x + 200, y + 255, 105, 1, seed=2620)
            else:
                calendar_icon(ctx, x + 70, y + 160, 260, 200, 1, seed=2630, marks=['x', 'o', 'x', 'o', 'x', 'o', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'o'], t=t, t0=t0 + .4)
                ink(ctx, [(x + 92, y + 382), (x + 108, y + 398)], 2.6, RED, 1, sketch=False); ink(ctx, [(x + 108, y + 382), (x + 92, y + 398)], 2.6, RED, 1, sketch=False)
                text(ctx, "train", x + 118, y + 400, 'hand', 30, INK_SOFT, 1, 'left')
                ink(ctx, ellipse_pts(x + 232, y + 390, 9, 9, 16), 2.4, TEAL, 1, closed=True, sketch=False)
                text(ctx, "rest", x + 248, y + 400, 'hand', 30, INK_SOFT, 1, 'left')
            text(ctx, l1, x + 200, y + 460, 'hand', 34, INK, 1, 'center')
            text(ctx, l2, x + 200, y + 505, 'hand', 34, INK_SOFT, 1, 'center')
            ctx.restore()
        s = ph(t, c("even") - .2, .7)
        if s > 0:
            caption_card(ctx, "one night of poor sleep can lower protein synthesis", 960, 990, t, c("even") - .2, size=40, seed=2640, t1=c("enough") + .6)


class Takeaway(Scene):
    sid = "s10_takeaway"
    extra = 0.6

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        chapter_tag(ctx, t, 9, "Moving vs. adapting")
        tf = c("workout") - .5  # "The workout isn't..."
        ga = 1 - ph(t, tf, .6)
        if ga > 0: self.graph(ctx, t, ga)
        fa = ph(t, tf, .7)
        if fa > 0: self.final(ctx, t, fa)

    def graph(self, ctx, t, a):
        c = self.cue
        x0, y0, w, h = 200, 860, 1520, 600
        axes(ctx, x0, y0, w, h, t, 0.3, xl="time", yl="capacity", a=a, seed=2700)
        # stage 1: simply moving vs adapting labels
        m = ph(t, c("simply") - .2, .6)
        base = .25
        # stage 2: stress / recovery / supercompensation single wave
        def wave(x):
            if x < .05: return base
            u = (x - .05) / .3
            if u > 1: return base + .08
            return base - .12 * math.sin(u * math.pi) * (u < .5) + (.08 * ease((u - .5) / .5) - .12 * math.sin(u * math.pi) * 0) * (u >= .5) - (.12 * math.sin(u * math.pi) if u >= .5 else 0) * 0
        # plateau (same weight forever)
        pl = ph(t, c("lift") - .3, 1.8, ease)
        plateau = lambda x: base + .02 * math.sin(x * 60)
        if pl > 0:
            curve(ctx, plateau, x0, y0, w, h, t, c("lift") - .3, 2.0, INK_SOFT, 3, a * (1 - .5 * ph(t, c("challenge") - .5, .5)), seed=2710, x0=0, x1=1)
            for k in range(6):
                dumbbell_icon(ctx, x0 + 150 + k * 240, y0 - h * base + 60, .4, a * ph(t, c("lift") + k * .25, .4), seed=2720 + k)
            text(ctx, "same weight, same way: a plateau", x0 + w * .5, y0 - h * base + 118, 'hand', 40, INK_SOFT, a * ph(t, c("forever") - .3, .6), 'center', reveal=ph(t, c("forever") - .3, .8))
        # the asked-to-adapt wave
        wv = ph(t, c("your") - .2, .6) * (1 - ph(t, c("lift") - .5, .5))
        if wv > 0:
            def sc(x):
                u = (x - .1) / .6
                if u <= 0: return .3
                if u < .3: return .3 - .14 * math.sin(u / .3 * math.pi / 2)
                if u < .8: return .16 + .26 * ease((u - .3) / .5)
                return .42 - .04 * ease((u - .8) / .2)
            curve(ctx, sc, x0, y0, w, h, t, c("your") - .1, 2.4, RED, 5, a * wv, seed=2730, x0=0, x1=1)
            text(ctx, "challenge", x0 + w * .16, y0 - h * .08, 'hand', 40, INK, a * wv * ph(t, c("asked") - .2, .5), 'center')
            text(ctx, "recover", x0 + w * .42, y0 - h * .24, 'hand', 40, INK, a * wv * ph(t, c("something") - .2, .5), 'center')
            text(ctx, "adapt: a little beyond where you started", x0 + w * .7, y0 - h * .52, 'hand', 40, RED, a * wv * ph(t, c("ready") - .3, .5), 'center', reveal=ph(t, c("ready") - .3, .8))
        # staircase (progressive overload)
        st = ph(t, c("challenge") - .3, .5)
        if st > 0:
            steps = 5
            pts = []
            for k in range(steps):
                xs = k / steps; lv = .3 + k * .11
                pts += [(x0 + w * xs, y0 - h * lv), (x0 + w * (xs + .07), y0 - h * (lv - .07)), (x0 + w * (xs + .16), y0 - h * (lv + .11))]
            pts = catmull(pts, 6)
            ink(ctx, pts, 6, RED, a * st, prog=ph(t, c("challenge") - .2, c("recover") - c("challenge") + .8, lambda x: x), seed=2740, amp=.8)
            labs = [("close to its limit", c("close")), ("add a little more", c("add")), ("let it recover", c("recover"))]
            for i, (s, tt) in enumerate(labs):
                text(ctx, s, x0 + w * (.1 + i * .3), y0 - h * (.5 + i * .17) - 40, 'hand', 42, RED_D, a * ph(t, tt - .2, .5), 'center', reveal=ph(t, tt - .2, .7))
        # top titles: moving vs adapting
        if m > 0:
            text(ctx, "moving", 700, 180, 'title_i', 64, INK_SOFT, a * m, 'center')
            text(ctx, "vs.", 960, 180, 'serif_i', 50, INK_SOFT, a * m, 'center')
            text(ctx, "adapting", 1220, 180, 'title_i', 64, RED_D, a * ph(t, c("adapting") - .2, .6), 'center')
            sub = a * (1 - ph(t, c("your") - .3, .5))
            text(ctx, "doing the exercise", 700, 240, 'hand', 36, INK_SOFT, sub * m, 'center', reveal=m)
            text(ctx, "the body changing because of it", 1220, 240, 'hand', 36, RED_D, sub * ph(t, c("adapting"), .6), 'center', reveal=ph(t, c("adapting"), .8))

    def final(self, ctx, t, a):
        c = self.cue
        f = Figure(470, 480, .8)
        th = 0.9 + .15 * math.sin(t * .8)
        f.draw(ctx, t, theta=th, skin=1.0, peel=(f.P((40, 120))[0], f.P((40, 120))[1], 140 * ph(t, c("rebuilding") - .5, 1.0, eback) + 1), glow_biceps=.5 * ph(t, c("rebuilding"), 1.0), body_a=a)
        for i, (s1, s2, tt, col) in enumerate([("The workout", "is the message.", c("message") - .5, INK), ("The rebuilding", "is the answer.", c("answer") - .7, RED_D)]):
            p = ph(t, tt, .8, eback)
            if p <= 0: continue
            x, y = 1000, 300 + i * 330
            ctx.save(); ctx.translate(x + 380, y + 120); ctx.rotate((-.02 if i == 0 else .015)); ctx.scale(.9 + .1 * p, .9 + .1 * p); ctx.translate(-(x + 380), -(y + 120))
            paper_shape(ctx, rect_pts(x, y, 760, 250), CREAM if i == 0 else hexc('F6E9D2'), a * clamp(p), 2800 + i, shadow=.24)
            text(ctx, s1, x + 380, y + 110, 'title', 70, col, a, 'center')
            text(ctx, s2, x + 380, y + 185, 'serif_i', 54, col, a, 'center')
            ctx.restore()
        if t < c("message") - .5:
            text(ctx, "The workout isn't what", 1380, 440, 'title', 64, INK, a * ph(t, c("workout") - .3, .6), 'center', reveal=ph(t, c("workout") - .3, .8))
            text(ctx, "makes you stronger.", 1380, 530, 'title', 64, INK, a * ph(t, c("makes") - .3, .6), 'center', reveal=ph(t, c("makes") - .3, .8))


class EndCard(Scene):
    def __init__(self):
        super().__init__(); self.dur = 7.0

    def draw(self, ctx, t):
        background(ctx, t)
        a = win(t, 0.2, 6.6, .8, 1.2)
        for i, (col, y, h, d) in enumerate([(RED, 360, 22, 0.0), (OCHRE_L, 394, 10, .15), (TEAL_L, 700, 12, .3), (RED_L, 724, 7, .45)]):
            p = ph(t, .3 + d, 1.2, eout)
            x0 = lerp(-900, 0, p) if i % 2 == 0 else lerp(W + 900, 0, p)
            paper_shape(ctx, [(x0 + 300, y), (x0 + 1620, y - 4), (x0 + 1620, y + h), (x0 + 300, y + h + 3)], col, a, seed=3000 + i, shadow=.14, amp=2.2)
        text(ctx, "Under Tension", 960, 560, 'title', 130, INK, a, 'center', reveal=ph(t, .6, 1.4, ease), rise=8)
        text(ctx, "train  ·  eat  ·  sleep  ·  repeat", 960, 640, 'serif_i', 46, INK_SOFT, a * ph(t, 1.8, 1.0), 'center', reveal=ph(t, 1.8, 1.4))
        set_c(ctx, PAPER, ph(t, 6.2, .8)); ctx.paint()
