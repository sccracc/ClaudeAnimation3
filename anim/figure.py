"""The hero illustration: a side-view human bust with an anatomical arm doing a curl."""
from .core import *

BODY = [(-95, -330), (-80, -380), (-30, -405), (30, -397), (60, -362), (68, -333), (64, -318), (84, -288), (70, -279),
        (73, -263), (66, -252), (70, -238), (56, -221), (22, -214), (8, -198), (12, -150), (45, -100), (78, -40),
        (88, 40), (74, 140), (78, 250), (62, 340), (60, 470), (-150, 470), (-152, 320), (-132, 160), (-150, 20),
        (-122, -108), (-78, -168), (-70, -228), (-100, -282)]
S = (-35, -45)  # shoulder joint
L1, L2 = 285, 255

def _pt(o, sc, p): return (o[0] + p[0] * sc, o[1] + p[1] * sc)

def arm_geom(theta, grow=0.0):
    """joint positions in local coords; theta=0 forearm hangs down, pi/2 = horizontal forward"""
    E = (S[0] + 12, S[1] + L1)
    d = (math.sin(theta), math.cos(theta))
    Hn = (E[0] + d[0] * L2, E[1] + d[1] * L2)
    return E, d, Hn

def taper(a, b, wa, wb, n=10):
    """closed polygon of a tapered capsule from a to b"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = []
    for i in range(n + 1):  # cap around b: from +normal side to -normal side through the tip
        q = ang + math.pi / 2 - math.pi * i / n
        pts.append((b[0] + math.cos(q) * wb / 2, b[1] + math.sin(q) * wb / 2))
    for i in range(n + 1):  # cap around a
        q = ang - math.pi / 2 - math.pi * i / n
        pts.append((a[0] + math.cos(q) * wa / 2, a[1] + math.sin(q) * wa / 2))
    return pts

def spindle(a, b, width, bow=0.0, n=28, tendon=0.14, side_bias=0.0):
    """muscle belly shape between a and b; bow bends it toward normal"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); nx, ny = -math.sin(ang), math.cos(ang)
    mid = ((a[0] + b[0]) / 2 + nx * bow, (a[1] + b[1]) / 2 + ny * bow)
    cl = qbez(a, mid, b, n)
    L, R = [], []
    for i, p in enumerate(cl):
        s = i / n
        w = width * (max(0, math.sin(math.pi * clamp((s - tendon * .3) / (1 - tendon * .6)))) ** 0.75) + 4
        L.append((p[0] + nx * w * (0.5 + side_bias), p[1] + ny * w * (0.5 + side_bias)))
        R.append((p[0] - nx * w * (0.5 - side_bias), p[1] - ny * w * (0.5 - side_bias)))
    return L + R[::-1], cl

def bone(a, b, w, knob=1.6):
    """bone: shaft with knobby ends"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); nx, ny = -math.sin(ang), math.cos(ang)
    ux, uy = math.cos(ang), math.sin(ang)
    pts = []
    for (p, sgn) in [(a, -1), (b, 1)]:
        pass
    L = math.dist(a, b)
    prof = [(0, w * knob * .5), (w * .5, w * knob * .55), (w * 1.3, w * .5), (L * .5, w * .42), (L - w * 1.3, w * .5), (L - w * .5, w * knob * .55), (L, w * knob * .5)]
    top = [(a[0] + ux * s + nx * r, a[1] + uy * s + ny * r) for s, r in prof]
    bot = [(a[0] + ux * s - nx * r, a[1] + uy * s - ny * r) for s, r in prof]
    endb = [(b[0] + ux * w * .35 * math.sin(math.pi * i / 6) + nx * w * knob * .5 * math.cos(math.pi * i / 6),
             b[1] + uy * w * .35 * math.sin(math.pi * i / 6) + ny * w * knob * .5 * math.cos(math.pi * i / 6)) for i in range(7)]
    enda = [(a[0] - ux * w * .35 * math.sin(math.pi * i / 6) - nx * w * knob * .5 * math.cos(math.pi * i / 6),
             a[1] - uy * w * .35 * math.sin(math.pi * i / 6) - ny * w * knob * .5 * math.cos(math.pi * i / 6)) for i in range(7)]
    return catmull(top + endb[1:-1] + bot[::-1] + enda[1:-1], 4, closed=True)

class Figure:
    def __init__(self, ox=560, oy=560, sc=1.0):
        self.o = (ox, oy); self.sc = sc

    def P(self, p): return _pt(self.o, self.sc, p)
    def PL(self, pts): return [self.P(p) for p in pts]

    def biceps_geom(self, theta, grow=0.0):
        E, d, Hn = arm_geom(theta)
        O = (S[0] + 20, S[1] + 18)
        I = (E[0] + d[0] * 38 + 10 * d[1], E[1] + d[1] * 38 - 10 * d[0])
        L = math.dist(O, I); L0 = L1 + 10
        bulge = (L0 / max(L, 120)) ** 0.8
        w = 76 * bulge * (1 + grow * .35)
        shape, cl = spindle(O, I, w, bow=-(18 + 26 * (bulge - 1)) * (1 + grow * .3), side_bias=0.0)
        return shape, cl, bulge

    def draw(self, ctx, t, theta=0.0, skin=1.0, bones=1.0, muscles=1.0, body_a=1.0, grow=0.0, glow_biceps=0.0,
             brain=0.0, nerve=0.0, pulse=None, dumbbell=1.0, hide_body_fill=False, peel=None, body_col=SLATE_L):
        sc = self.sc
        E, d, Hn = arm_geom(theta)
        # ---- body silhouette (cut paper)
        if body_a > 0:
            paper_shape(ctx, self.PL(catmull(BODY, 8, closed=True)), body_col, body_a, seed=11, shadow=.2, sh_off=(6, 8), amp=1.4)
            # soft pencil contour on face / chest
            ink(ctx, self.PL(catmull(BODY[3:22], 8)), 1.6, INK_SOFT, .55 * body_a, seed=12)
            # eye + ear hints
            ex, ey = self.P((38, -322)); ink(ctx, [(ex - 7, ey), (ex + 6, ey + 1)], 2.2, INK_SOFT, .6 * body_a, sketch=False)
            ear = self.PL(ellipse_pts(-32, -300, 13, 22, 20))
            ink(ctx, ear[4:18], 1.8, INK_SOFT, .45 * body_a, seed=3)
        # ---- brain sketch
        if brain > 0:
            bx, by = self.P((-18, -335)); r = 58 * sc
            pts = ellipse_pts(bx, by, r * 1.15, r * .8, 50, -.05)
            paper_shape(ctx, pts, BLUSH, brain, seed=21, shadow=.12, grain=.8)
            # cerebellum
            paper_shape(ctx, ellipse_pts(bx - r * .7, by + r * .62, r * .42, r * .28, 30, .3), mix(BLUSH, RED_L, .4), brain, seed=23, shadow=.08)
            for k in range(3):
                ink(ctx, ellipse_pts(bx - r * .7, by + r * .62, r * (.34 - k * .1), r * (.2 - k * .06), 20, .3, .4, 2.8), 1.1, RED_D, .5 * brain, seed=24 + k)
            for k in range(6):  # gyri: meandering folds following the outline
                rr = .82 - k * .13
                sq = [(bx + math.cos(a0) * r * 1.1 * rr + math.sin(a0 * 9 + k) * r * .06,
                       by + math.sin(a0) * r * .75 * rr + math.cos(a0 * 9 + k * 2) * r * .06) for a0 in [-2.9 + j * .16 + k * .3 for j in range(22 - k * 2)]]
                ink(ctx, catmull(sq, 3), 1.3, RED_D, .5 * brain, seed=k)
            ink(ctx, [(bx - r * .15, by - r * .75), (bx - r * .05, by - r * .2), (bx - r * .25, by + r * .3)], 1.5, RED_D, .55 * brain, seed=30)
            ink(ctx, pts, 1.8, RED_D, .7 * brain, seed=22, closed=True)
        # ---- arm: skin layer vs anatomy
        skin_parts = self._skin_polys(theta, grow)
        self._noskin = 1 - skin if peel is None else 1.0
        if muscles > 0 or bones > 0:
            self._anatomy(ctx, t, theta, muscles, bones, grow, glow_biceps)
        if nerve > 0:
            self._nerve(ctx, t, theta, nerve, pulse)
        if skin > 0:
            ctx.save()
            if peel is not None:  # peel: (cx, cy, r) window torn open in the skin
                cx, cy, r = peel
                win_pts = jitter(ellipse_pts(cx, cy, r * 1.25, r, 70, -.4), r * .06 + 1, .02, 5, True, boil_on=False)
                ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
                ctx.rectangle(-4000, -4000, 9000, 9000); path(ctx, win_pts, True); ctx.clip()
            ctx.push_group()
            for poly in skin_parts:
                set_c(ctx, BLUSH); path(ctx, jitter(poly, 1.3, .03, 31, True, step=6), True); ctx.set_line_width(16); ctx.fill_preserve(); ctx.stroke()
            grp = ctx.pop_group()
            # shadow
            ctx.save(); ctx.translate(6, 9); ctx.set_source_rgba(.18, .12, .09, .22 * skin); ctx.mask(grp); ctx.restore()
            ctx.save(); ctx.set_source_rgba(*mix(BLUSH, SLATE_L, .0)[:3], skin); ctx.mask(grp); ctx.restore()
            ctx.push_group(); ctx.set_source(grp); ctx.paint(); ctx.set_operator(cairo.OPERATOR_IN); grain_fill(ctx, 1.0, op=cairo.OPERATOR_IN); g2 = ctx.pop_group()
            ctx.save(); ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT); ctx.set_source(g2); ctx.paint_with_alpha(skin * .9); ctx.restore()
            ctx.restore()
            if peel is not None:
                ctx.push_group()
                ink(ctx, win_pts, 3.2, CREAM, .95 * skin, seed=6, closed=True, sketch=False)
                ink(ctx, win_pts, 1.3, INK_SOFT, .55 * skin, seed=7, closed=True)
                rim = ctx.pop_group(); ctx.set_source(rim); ctx.mask(grp)
            # outline of the arm skin (only outer)
            self._hand_and_weight(ctx, theta, dumbbell, skin_on=True)
        else:
            self._hand_and_weight(ctx, theta, dumbbell, skin_on=False)

    def _skin_polys(self, theta, grow):
        E, d, Hn = arm_geom(theta)
        _, _, bulge = self.biceps_geom(theta, grow)
        up = taper(self.P((S[0] - 5, S[1] - 20)), self.P(E), 128 * self.sc, 84 * self.sc)
        # biceps bulge on the front of the upper arm
        bshape, _, _ = self.biceps_geom(theta, grow)
        b2 = [self.P((x + 6, y)) for x, y in bshape]
        fo = taper(self.P(E), self.P(Hn), 82 * self.sc, 58 * self.sc)
        sh = self.PL(ellipse_pts(S[0] - 6, S[1] - 6, 72, 66, 40))
        return [up, b2, fo, sh]

    def _anatomy(self, ctx, t, theta, muscles, bones, grow, glow_biceps):
        E, d, Hn = arm_geom(theta)
        sc = self.sc
        if bones > 0:
            # scapula hint + clavicle
            paper_shape(ctx, self.PL(catmull([(-120, -95), (-60, -80), (-40, -30), (-95, 90), (-128, 40)], 6, True)), BONE, bones * .8 * self._noskin, seed=40, shadow=.1, outline=INK_SOFT, ow=1.4, grain=.6)
            hum = bone(self.P((S[0], S[1] + 5)), self.P((E[0], E[1] - 6)), 30 * sc)
            paper_shape(ctx, hum, BONE, bones, seed=41, shadow=.15, outline=INK, ow=1.8, grain=.6)
            # radius & ulna
            off = (d[1] * 9, -d[0] * 9)
            ul = bone(self.P((E[0] - off[0], E[1] - off[1])), self.P((Hn[0] - off[0] - d[0] * 25, Hn[1] - off[1] - d[1] * 25)), 20 * sc, 1.5)
            ra = bone(self.P((E[0] + off[0] + d[0] * 8, E[1] + off[1] + d[1] * 8)), self.P((Hn[0] + off[0] - d[0] * 20, Hn[1] + off[1] - d[1] * 20)), 19 * sc, 1.5)
            paper_shape(ctx, ul, BONE, bones, seed=42, shadow=.12, outline=INK, ow=1.6, grain=.6)
            paper_shape(ctx, ra, mix(BONE, PAPER_D, .3), bones, seed=43, shadow=.12, outline=INK, ow=1.6, grain=.6)
        if muscles > 0:
            m = muscles
            # triceps on the back of the upper arm
            tri, _ = spindle(self.P((S[0] - 30, S[1] + 10)), self.P((E[0] - 22 - d[0] * 10, E[1] + 4)), 58 * sc * (1 - .15 * clamp(theta / 2.2)), bow=12 * sc)
            paper_shape(ctx, tri, RED_D, m, seed=50, shadow=.18, hatch=INK, hatch_a=.14, grain=1.0)
            # forearm flexors
            fa, _ = spindle(self.P((E[0] + 4, E[1] - 6)), self.P((Hn[0] - d[0] * 30, Hn[1] - d[1] * 30)), 48 * sc, bow=-8 * sc)
            paper_shape(ctx, fa, mix(RED, RED_L, .35), m, seed=51, shadow=.16, grain=1.0)
            # deltoid cap
            dl = self.PL(catmull([(-88, -70), (-35, -98), (22, -62), (14, 18), (-18, 62), (-62, 10)], 6, True))
            paper_shape(ctx, dl, mix(RED, RED_D, .35), m, seed=52, shadow=.2, grain=1.0, hatch=INK, hatch_a=.1)
            # biceps
            bs, cl, bulge = self.biceps_geom(theta, grow)
            if glow_biceps > 0:
                c = self.P(cl[len(cl) // 2]); glow(ctx, c[0], c[1], 190 * sc, OCHRE, glow_biceps)
            paper_shape(ctx, self.PL(bs), RED, m, seed=53, shadow=.24, grain=1.0, shade=.22, shade_dir=(-.8, .6))
            # fiber striations along the biceps
            for k in range(-3, 4):
                ln = [self.P((p[0] + k * 6 * bulge * (math.sin(math.pi * i / (len(cl) - 1))) , p[1])) for i, p in enumerate(cl)]
                ink(ctx, ln[3:-3], 1.1, RED_D, .45 * m, seed=60 + k, sketch=False, amp=.8)
            # tendons
            ink(ctx, self.PL([cl[0], (S[0] + 10, S[1] - 10)]), 3, BONE, m, seed=61, sketch=False)

    def _nerve(self, ctx, t, theta, a, pulse):
        pts = self.nerve_path(theta)
        ink(ctx, pts, 2.2, OCHRE, a * .9, seed=70, amp=.8)
        ink(ctx, pts, 5.5, OCHRE, a * .15, seed=71, sketch=False)
        if pulse is not None:
            for pp in (pulse if isinstance(pulse, (list, tuple)) else [pulse]):
                if 0 <= pp <= 1:
                    x, y = point_at(pts, pp)
                    glow(ctx, x, y, 60, OCHRE_L, 1.0); dots(ctx, [(x, y)], 7, CREAM, 1)

    def nerve_path(self, theta):
        E, d, Hn = arm_geom(theta)
        _, cl, _ = self.biceps_geom(theta)
        mid = cl[len(cl) // 2]
        return self.PL(catmull([(-18, -320), (-40, -250), (-75, -170), (-80, -100), (-55, -40), (-10, 20), (mid[0] - 15, mid[1] - 20), mid], 10))

    def _hand_and_weight(self, ctx, theta, a, skin_on):
        E, d, Hn = arm_geom(theta)
        sc = self.sc
        hc = (Hn[0] + d[0] * 18, Hn[1] + d[1] * 18)
        # fist
        fist = self.PL(catmull([(hc[0] + d[1] * 30 - d[0] * 22, hc[1] - d[0] * 30 - d[1] * 22), (hc[0] + d[1] * 34 + d[0] * 14, hc[1] - d[0] * 34 + d[1] * 14),
                                (hc[0] - d[1] * 5 + d[0] * 36, hc[1] + d[0] * 5 + d[1] * 36), (hc[0] - d[1] * 34 + d[0] * 10, hc[1] + d[0] * 34 + d[1] * 10),
                                (hc[0] - d[1] * 30 - d[0] * 22, hc[1] + d[0] * 30 - d[1] * 22)], 6, True))
        paper_shape(ctx, fist, BLUSH, 1.0, seed=83, shadow=.18, grain=1.0, outline=INK_SOFT, ow=1.3)
        if a > 0:
            # dumbbell seen end-on: plate disc + handle hub
            cx, cy = self.P((hc[0] + d[0] * 6, hc[1] + d[1] * 6))
            blob(ctx, cx, cy, 56 * sc, INK_SOFT, a, seed=80, shadow=.25, grain=1.0)
            ink(ctx, ellipse_pts(cx, cy, 43 * sc, 43 * sc, 40), 1.6, CREAM, .35 * a, seed=81, closed=True)
            ink(ctx, ellipse_pts(cx, cy, 14 * sc, 14 * sc, 20), 1.6, CREAM, .45 * a, seed=82, closed=True)

