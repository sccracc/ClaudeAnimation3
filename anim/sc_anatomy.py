from .core import *
from .scene import *
from .assets import *

class Anatomy(Scene):
    sid = "s02_anatomy"

    def draw(self, ctx, t):
        c = self.cue
        background(ctx, t)
        z1, z2, z3 = c("each") - .5, c("inside", 2) - .45, c("this") - .35
        self.t = t
        def A(ctx): self.layerA(ctx, t)
        def B(ctx): self.layerB(ctx, t)
        def C(ctx): self.layerC(ctx, t)
        def D(ctx): self.layerD(ctx, t)
        if t < z1 + 1.3:
            zoom_through(ctx, t, z1, 1.3, self.fas_focus, A, B, zmax=7, bg_t=t)
        elif t < z2 + 1.3:
            zoom_through(ctx, t, z2, 1.3, (980, 545), B, C, zmax=5, bg_t=t)
        else:
            zoom_through(ctx, t, z3, 1.3, self.sarc_focus, C, D, zmax=6, bg_t=t)
        chapter_tag(ctx, t, 1, "What muscle is made of")

    def sfx(self):
        c = self.cue
        return [(c("each") - .5, 'zoom'), (c("inside", 2) - .45, 'zoom'), (c("this") - .35, 'zoom')]

    fas_focus = (1500, 470)
    sarc_focus = (960, 640)

    def layerA(self, ctx, t):
        c = self.cue
        ent = ph(t, 0.1, 1.0, eout)
        x0, x1, cy = 230, 1190, 500
        ctx.save(); ctx.translate((1 - ent) * -80, 0)
        muscle_belly(ctx, x0, x1, cy, 250, ent, seed=200)
        ctx.restore()
        label(ctx, "biceps brachii", 560, 300, 700, 430, t, c("biceps") - .2, font='serif_i', size=46, seed=1)
        # rope sketch
        ra = ph(t, c("rope") - .3, .6)
        if ra > 0:
            rx, ry = 330, 820
            for k in range(3):
                pts = [(rx + i * 8, ry + math.sin(i * .35 + k * 2.1) * 16) for i in range(70)]
                ink(ctx, pts, 7, [OCHRE, mix(OCHRE, RED_D, .3), OCHRE_L][k], ra, prog=ra, seed=210 + k, sketch=False)
                ink(ctx, pts, 1.2, INK_SOFT, ra * .6, prog=ra, seed=213 + k, sketch=False)
            text(ctx, "built like a rope", rx + 600, ry + 12, 'hand', 44, INK, ra, reveal=ph(t, c("rope"), .8))
        # cross-section callout
        cs_t = c("bundles") - .3
        pa = ph(t, cs_t, .6)
        if pa > 0:
            for yy in (-1, 1):
                ink(ctx, [(x1 + 10, cy + yy * 30), (1500 - 40, 470 + yy * 225)], 1.6, INK_SOFT, pa * .7, prog=pa, seed=220 + yy, dash=[7, 7])
            ink(ctx, ellipse_pts(x1 - 10, cy, 26, 62, 40), 2, INK_SOFT, pa * .8, prog=pa, seed=223, closed=True)
        shown = cross_section(ctx, 1500, 470, 235, t, cs_t, seed=230, fibers_t=c("bundles", 2) - .2, highlight=3 if t > c("each") - 1.2 else None)
        if len(shown) > 3: self.fas_focus = shown[3][:2]
        label(ctx, "bundles of fibers", 1330, 800, 1450, 640, t, c("inside") + .1, size=40, seed=2)

    def layerB(self, ctx, t):
        c = self.cue
        t0 = c("each") + .5
        ys = [330, 440, 550, 660, 770]
        self.nuc = None
        for i, y in enumerate(ys):
            nl = fiber_tube(ctx, 150 + (i % 2) * 40, 1780 - (i % 3) * 30, y, 92, 1.0, seed=300 + i, prog=ph(t, t0 - 1.2 + i * .12, 1.8, ease))
            if i == 0 and nl and len(nl) > 8: self.nuc = nl[8]
        label(ctx, "one muscle fiber = one long cell", 640, 190, 700, 440 - 46, t, c("single") - .2, font='serif_i', size=46, seed=3)
        la = ph(t, c("length") - .3, 1.0, ease)
        if la > 0:
            arrow(ctx, [(170, 900), (1760, 900)], 2.6, RED, 1, prog=la, seed=310, both=True)
            text(ctx, "can run nearly the full length of the muscle", 960, 960, 'hand', 44, RED, 1, 'center', reveal=ph(t, c("length"), .9))
        nu = ph(t, c("cells") + .3, .6)
        if self.nuc:
            label(ctx, "nuclei", self.nuc[0] + 60, 230, self.nuc[0], self.nuc[1] - 8, t, c("cells") + .2, size=38, seed=4, a=1.0)

    def layerC(self, ctx, t):
        c = self.cue
        t0 = c("inside", 2) + .6
        fiber_tube(ctx, -60, 1160, 300, 250, 1.0, seed=400, nuclei=True, stri_sp=14)
        # cut face at the end of the fiber showing myofibrils in cross-section
        ex = 1160
        paper_shape(ctx, ellipse_pts(ex, 300, 45, 125, 50), mix(RED, BLUSH, .45), 1, seed=401, shadow=.15, grain=.8)
        for j, (u, v, rr) in enumerate(packed_circles(1.0, .13, 5, 40)):
            dots(ctx, [(ex + u * 40, 300 + v * 115)], rr * 70, RED, .9)
            ink(ctx, ellipse_pts(ex + u * 40, 300 + v * 115, rr * 70, rr * 115, 12), 1.0, RED_D, .7, seed=410 + j, closed=True, sketch=False)
        # myofibrils drawn out of the cut end, sweeping down and across
        rows = [560, 640, 720, 800]
        for i, y in enumerate(rows):
            p = ph(t, t0 + i * .15, 1.4, ease)
            if p <= 0: continue
            ink(ctx, bez((ex + 20, 300 + (i - 1.5) * 40), (ex + 200, 320 + (i - 1.5) * 40), (1860, y - 160), (1840, y - 40), 20), 3, RED_L, .5 * p * (1 - ph(t, t0 + 2.5, 1.0)), prog=p, seed=420 + i, sketch=False)
            myofibril(ctx, 90, 1840, y, 46, 1, seed=430 + i, period=132, prog=p,
                      hl=6 if (i == 1 and t > c("sarcomeres") - .2) else None)
        label(ctx, "myofibrils", 400, 480, 520, 560 - 23, t, c("myofibrils") - .3, font='serif_i', size=48, seed=5)
        # bands note + sarcomere bracket
        ra = ph(t, c("repeating") - .2, .6)
        if ra > 0:
            for k in range(13):
                xk = 90 + k * 132
                ink(ctx, [(xk, 590), (xk, 602)], 2, INK, ra * (.9 if k in (6, 7) else .35), seed=440 + k, sketch=False)
        sa = ph(t, c("sarcomeres") - .2, .7, ease)
        if sa > 0:
            xa, xb = 90 + 6 * 132, 90 + 7 * 132
            ink(ctx, [(xa, 585), (xa, 570), (xb, 570), (xb, 585)], 3, RED, sa, prog=sa, seed=450, sketch=False)
            text(ctx, "sarcomere", (xa + xb) / 2, 548, 'serif_i', 50, RED, sa, 'center', reveal=sa)
            self.sarc_focus = ((xa + xb) / 2, 640)
        self.sarc_focus = (90 + 6.5 * 132, 640)

    def layerD(self, ctx, t):
        c = self.cue
        t0 = c("this")
        zl, zr, yt, yb = sarcomere(ctx, 960, 540, t, 0.0, 1.0, scale=1.1, seed=500, rows=2)
        # bracket for one sarcomere
        ba = ph(t, c("sarcomere") - .2, .8, ease)
        if ba > 0:
            ink(ctx, [(zl, yt - 50), (zl, yt - 70), (zr, yt - 70), (zr, yt - 50)], 3, INK, ba, prog=ba, seed=510, sketch=False)
            text(ctx, "one sarcomere", 960, yt - 92, 'serif_i', 52, INK, ba, 'center', reveal=ba)
        label(ctx, "Z-disc", zl - 150, yb + 110, zl, yb + 10, t, c("holds") + .1, font='serif_i', size=42, seed=6, align='left')
        label(ctx, "Z-disc", zr + 40, yb + 110, zr, yb + 10, t, c("holds") + .3, font='serif_i', size=42, seed=7, align='left')
        label(ctx, "actin  (thin filament)", 520, yb + 170, zl + 170, 540 + 2 * 86, t, c("actin") - .3, font='serif_i', size=46, c=hexc('9A6420'), seed=8)
        label(ctx, "myosin  (thick filament)", 1080, yb + 170, 1100, 540 + 1.5 * 86 - 10, t, c("myosin") - .3, font='serif_i', size=46, c=RED_D, seed=9)
        # gentle highlight pulses on the named filament type
        if t > c("actin") - .3 and t < c("thicker"):
            glow(ctx, zl + 180, 560, 260, OCHRE_L, .35 * win(t, c("actin") - .3, c("thicker"), .4, .4))
        if t > c("thicker") - .2:
            glow(ctx, 960, 560, 330, RED_L, .3 * win(t, c("thicker") - .2, 1e9, .4, .4))
